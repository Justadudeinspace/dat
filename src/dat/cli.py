"""Command line interface for the Dev Audit Tool."""
from __future__ import annotations

import argparse
import asyncio
import getpass
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List

from rich.console import Console
from rich.table import Table

from .integration.lrc import load_integration_config, select_schema
from .integration.signing import sign_artifact
from .logging.audit import append_encrypted_log
from .pdf.report import export_pdf
from .scanner.core import ScanReport, build_scan_report

console = Console()


def parse_arguments(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Enterprise Dev Audit Tool")
    parser.add_argument("path", nargs="?", default=".", help="Target directory")
    parser.add_argument("-s", "--safe", action="store_true", help="Enable safe mode (skip large files)")
    parser.add_argument("-p", "--deep", action="store_true", help="Deep scan including binary formats")
    parser.add_argument("-i", "--ignore", action="append", default=[], help="Glob pattern to ignore")
    parser.add_argument(
        "-o",
        "--report",
        help="Output path for report (supports .jsonl, .json, .pdf)",
    )
    parser.add_argument("--jsonl", help="Write JSONL report to the given path")
    parser.add_argument("--pdf", help="Write PDF report to the given path")
    parser.add_argument("--diff", help="Compare the scan with a previous JSON report")
    parser.add_argument("--from-lrc", nargs="?", const="auto", help="Load LRC metadata and policy")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--no-sign", action="store_true", help="Disable artifact signing")
    return parser.parse_args(argv)


def confirm(message: str) -> bool:
    response = console.input(f"[cyan]?[/cyan] {message} [y/N]: ")
    return response.strip().lower() in {"y", "yes"}


async def run_cli(argv: List[str]) -> int:
    args = parse_arguments(argv)
    target = Path(args.path).expanduser().resolve()

    if args.interactive and not confirm(f"Scan repository at {target}?"):
        console.print("[yellow]Aborted by user[/yellow]")
        return 1

    if not target.exists():
        console.print(f"[red]Path not found:[/red] {target}")
        return 2

    schema = None
    if args.from_lrc is not None:
        config_path = None if args.from_lrc == "auto" else Path(args.from_lrc)
        config = load_integration_config(config_path)
        schema = select_schema(config, target.name)

    report = await build_scan_report(target, ignore=args.ignore, safe=args.safe, deep=args.deep, schema=schema)
    fingerprint = _fingerprint(report)

    display_report(report, fingerprint)

    outputs: List[Path] = []
    maybe = args.report
    if maybe:
        outputs.append(write_report(report, Path(maybe), fingerprint))
    if args.jsonl:
        outputs.append(write_report(report, Path(args.jsonl), fingerprint, fmt="jsonl"))
    if args.pdf:
        outputs.append(write_report(report, Path(args.pdf), fingerprint, fmt="pdf"))
    if not outputs:
        # Default JSONL in working directory
        outputs.append(write_report(report, target / "dat-report.jsonl", fingerprint, fmt="jsonl"))

    if args.diff:
        compare_reports(report, Path(args.diff))

    for output in outputs:
        if not args.no_sign:
            signature = sign_artifact(output)
            console.print(f"[green]Signed[/green] {output} -> {signature}")

    append_encrypted_log(
        {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "user": getpass.getuser(),
            "repo": report.repo,
            "fingerprint": fingerprint,
            "artifacts": [str(path) for path in outputs],
        }
    )

    return 0


def _fingerprint(report: ScanReport) -> str:
    payload = report.to_json().encode("utf-8")
    return __import__("hashlib").sha256(payload).hexdigest()


def write_report(report: ScanReport, destination: Path, fingerprint: str, fmt: str | None = None) -> Path:
    fmt = fmt or destination.suffix.lstrip(".")
    destination = destination.expanduser()
    destination.parent.mkdir(parents=True, exist_ok=True)
    if fmt in {"json", "jsonl"}:
        payload = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "user": getpass.getuser(),
            "repo": report.repo,
            "fingerprint": fingerprint,
            "report": report.to_dict(),
        }
        with destination.open("w", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, sort_keys=True))
            if fmt == "jsonl":
                handle.write("\n")
        console.print(f"[green]JSON report written:[/green] {destination}")
        return destination
    if fmt == "pdf":
        export_pdf(report, destination)
        console.print(f"[green]PDF report written:[/green] {destination}")
        return destination
    raise ValueError(f"Unsupported report format: {fmt}")


def display_report(report: ScanReport, fingerprint: str) -> None:
    table = Table(title=f"DAT scan for {report.repo}")
    table.add_column("Path", style="cyan")
    table.add_column("Size", justify="right")
    table.add_column("Issues", justify="right")

    for file_report in report.files[:20]:
        table.add_row(file_report.path, str(file_report.size), str(len(file_report.violations)))
    if len(report.files) > 20:
        table.add_row("…", "…", "…")
    console.print(table)
    console.print(
        f"[bold]Fingerprint:[/bold] {fingerprint}  [bold]Files:[/bold] {len(report.files)}  [bold]Violations:[/bold] {sum(len(f.violations) for f in report.files)}"
    )


def compare_reports(report: ScanReport, previous_path: Path) -> None:
    if not previous_path.exists():
        console.print(f"[yellow]Previous report not found:[/yellow] {previous_path}")
        return
    try:
        payload = json.loads(previous_path.read_text(encoding="utf-8").splitlines()[0])
    except Exception as exc:  # pragma: no cover - invalid file is rare
        console.print(f"[red]Failed to read previous report:[/red] {exc}")
        return
    before = {entry["path"]: entry for entry in payload.get("report", {}).get("files", [])}
    after = {file_report.path: file_report for file_report in report.files}
    regressions = []
    for path, current in after.items():
        previous = before.get(path)
        if not previous:
            continue
        prev_issues = len(previous.get("violations", []))
        now_issues = len(current.violations)
        if now_issues > prev_issues:
            regressions.append((path, prev_issues, now_issues))
    if not regressions:
        console.print("[green]No new regressions detected against baseline[/green]")
        return
    table = Table(title="Policy regressions")
    table.add_column("Path")
    table.add_column("Previous")
    table.add_column("Current")
    for path, before_count, after_count in regressions:
        table.add_row(path, str(before_count), str(after_count))
    console.print(table)


def main(argv: List[str] | None = None) -> int:
    try:
        return asyncio.run(run_cli(list(argv or sys.argv[1:])))
    except KeyboardInterrupt:  # pragma: no cover - interactive
        console.print("[yellow]Interrupted[/yellow]")
        return 130


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
