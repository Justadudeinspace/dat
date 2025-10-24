"""Command line interface for the Enterprise Dev Audit Tool."""
from __future__ import annotations

import argparse
import asyncio
import getpass
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Sequence

from rich.console import Console
from rich.table import Table

from . import __version__
from .integration.lrc import load_integration_config, select_schema
from .integration.signing import sign_artifact
from .logging.audit import append_encrypted_log
from .pdf.report import export_pdf
from .scanner.core import ScanReport, build_scan_report

console = Console()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Enterprise Dev Audit Tool")
    parser.add_argument("path", nargs="?", default=".", help="Target directory to scan")
    parser.add_argument("--from-lrc", nargs="?", const="auto", 
                       help="Load LRC metadata and policy (auto-detects if no path provided)")
    parser.add_argument("-i", "--ignore", action="append", default=[], 
                       help="Glob pattern to ignore")
    parser.add_argument("--max-lines", type=int, default=1000, 
                       help="Maximum lines per file in safe mode")
    parser.add_argument("--max-size", type=int, default=10 * 1024 * 1024, 
                       help="Maximum file size in safe mode")
    parser.add_argument("-s", "--safe", dest="safe", action="store_true", 
                       help="Enable safe scanning (skip large files)")
    parser.add_argument("--no-safe", dest="safe", action="store_false", 
                       help="Disable safe scanning")
    parser.set_defaults(safe=True)
    parser.add_argument("-p", "--deep", action="store_true", 
                       help="Deep scan including binary formats (overrides safe limits)")
    parser.add_argument("-o", "--output", type=str, 
                       help="Output path for report (supports .jsonl, .json, .pdf)")
    parser.add_argument("--jsonl", help="Write JSONL report to the given path")
    parser.add_argument("--pdf", help="Write PDF report to the given path")
    parser.add_argument("--report", type=str, help="Alias for --output")
    parser.add_argument("--diff", type=str, help="Compare against a previous JSON report")
    parser.add_argument("--interactive", action="store_true", 
                       help="Run in interactive mode with confirmation prompts")
    parser.add_argument("--no-sign", action="store_true", 
                       help="Disable artifact signing")
    parser.add_argument("--sign", action="store_true", 
                       help="Sign generated reports with GPG")
    parser.add_argument("-v", "--verbose", action="store_true", 
                       help="Enable verbose console output")
    parser.add_argument("--version", action="store_true", 
                       help="Display version information")
    return parser


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = build_parser()
    args = parser.parse_args(argv)
    
    # Handle version flag
    if args.version:
        print(__version__)
        raise SystemExit(0)
        
    # Handle conflicting signing options
    if args.sign and args.no_sign:
        console.print("[red]Error: --sign and --no-sign are mutually exclusive[/red]")
        raise SystemExit(1)
        
    return args


def normalise_path(path: str) -> Path:
    """Normalize and resolve file paths."""
    return Path(path).expanduser().resolve()


def determine_safe_mode(args: argparse.Namespace) -> bool:
    """Determine if safe mode should be enabled."""
    if args.deep:
        return False
    return bool(args.safe)


def confirm(message: str) -> bool:
    """Get user confirmation in interactive mode."""
    response = console.input(f"[cyan]?[/cyan] {message} [y/N]: ")
    return response.strip().lower() in {"y", "yes"}


def _fingerprint(report: ScanReport) -> str:
    """Generate a fingerprint for the report."""
    payload = report.to_json().encode("utf-8")
    return __import__("hashlib").sha256(payload).hexdigest()


def write_report(report: ScanReport, destination: Path, fingerprint: str, 
                fmt: str | None = None) -> Path:
    """Write report in the specified format."""
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


def display_report(report: ScanReport, fingerprint: str, verbose: bool = False) -> None:
    """Display scan results in a rich table."""
    table = Table(title=f"DAT scan for {report.repo}")
    table.add_column("Path", style="cyan")
    table.add_column("Size", justify="right")
    table.add_column("Issues", justify="right")

    # Show files with violations first, then others
    files_with_issues = [f for f in report.files if f.violations]
    other_files = [f for f in report.files if not f.violations]
    
    display_files = files_with_issues + other_files
    
    for file_report in display_files[:20]:
        table.add_row(
            file_report.path, 
            str(file_report.size), 
            str(len(file_report.violations))
        )
        
    if len(display_files) > 20:
        table.add_row("…", "…", "…")
        
    console.print(table)
    
    total_violations = sum(len(f.violations) for f in report.files)
    console.print(
        f"[bold]Fingerprint:[/bold] {fingerprint}  "
        f"[bold]Files:[/bold] {len(report.files)}  "
        f"[bold]Violations:[/bold] {total_violations}"
    )
    
    if verbose and files_with_issues:
        console.print("\n[bold]Files with issues:[/bold]")
        for file_report in files_with_issues[:10]:  # Limit verbose output
            for violation in file_report.violations[:3]:  # Show first 3 violations per file
                console.print(f"  {file_report.path}: {violation}")


def compare_reports(report: ScanReport, previous_path: Path) -> None:
    """Compare current scan with a previous report."""
    if not previous_path.exists():
        console.print(f"[yellow]Previous report not found:[/yellow] {previous_path}")
        return
        
    try:
        payload = json.loads(previous_path.read_text(encoding="utf-8").splitlines()[0])
    except Exception as exc:
        console.print(f"[red]Failed to read previous report:[/red] {exc}")
        return
        
    before = {entry["path"]: entry for entry in payload.get("report", {}).get("files", [])}
    after = {file_report.path: file_report for file_report in report.files}
    
    regressions = []
    improvements = []
    new_files = []
    removed_files = []
    
    for path, current in after.items():
        previous = before.get(path)
        if not previous:
            new_files.append((path, len(current.violations)))
            continue
            
        prev_issues = len(previous.get("violations", []))
        now_issues = len(current.violations)
        
        if now_issues > prev_issues:
            regressions.append((path, prev_issues, now_issues))
        elif now_issues < prev_issues:
            improvements.append((path, prev_issues, now_issues))
    
    for path in before:
        if path not in after:
            removed_files.append((path, len(before[path].get("violations", []))))
    
    if not any([regressions, improvements, new_files, removed_files]):
        console.print("[green]No changes detected compared to baseline[/green]")
        return
        
    if regressions:
        table = Table(title="Policy Regressions")
        table.add_column("Path")
        table.add_column("Previous")
        table.add_column("Current")
        for path, before_count, after_count in regressions:
            table.add_row(path, str(before_count), str(after_count))
        console.print(table)
        
    if improvements:
        console.print(f"[green]Improvements in {len(improvements)} files[/green]")
        
    if new_files:
        console.print(f"[yellow]New files with issues: {len(new_files)}[/yellow]")
        
    if removed_files:
        console.print(f"[blue]Removed files: {len(removed_files)}[/blue]")


async def run_cli(argv: Sequence[str] | None = None) -> int:
    """Main CLI execution with async support."""
    try:
        args = parse_args(argv)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 1

    target = normalise_path(args.path)

    # Interactive confirmation
    if args.interactive and not confirm(f"Scan repository at {target}?"):
        console.print("[yellow]Scan aborted by user[/yellow]")
        return 1

    if not target.exists():
        console.print(f"[red]Path does not exist:[/red] {target}")
        return 2

    # Load LRC configuration if requested
    schema = None
    if args.from_lrc is not None:
        config_path = None if args.from_lrc == "auto" else Path(args.from_lrc)
        try:
            config = load_integration_config(config_path)
            schema = select_schema(config, target.name)
        except Exception as exc:
            console.print(f"[red]Failed to load LRC config:[/red] {exc}")
            if args.interactive and not confirm("Continue without LRC config?"):
                return 3

    # Build scan report
    try:
        report = await build_scan_report(
            target, 
            ignore=args.ignore, 
            safe=determine_safe_mode(args),
            deep=args.deep, 
            schema=schema,
            max_lines=args.max_lines,
            max_size=args.max_size
        )
    except Exception as exc:
        console.print(f"[red]Scan failed:[/red] {exc}")
        return 4

    fingerprint = _fingerprint(report)
    display_report(report, fingerprint, args.verbose)

    # Generate outputs
    outputs: List[Path] = []
    
    # Determine output format and paths
    output_paths = []
    if args.output:
        output_paths.append((args.output, None))
    if args.report:  # Alias for --output
        output_paths.append((args.report, None))
    if args.jsonl:
        output_paths.append((args.jsonl, "jsonl"))
    if args.pdf:
        output_paths.append((args.pdf, "pdf"))
        
    # If no outputs specified, create default JSONL
    if not output_paths and not args.diff:
        default_path = target / "dat-report.jsonl"
        output_paths.append((str(default_path), "jsonl"))

    # Write reports
    for path_str, fmt in output_paths:
        try:
            output_path = write_report(report, Path(path_str), fingerprint, fmt)
            outputs.append(output_path)
        except Exception as exc:
            console.print(f"[red]Failed to write report {path_str}:[/red] {exc}")
            if args.interactive and not confirm("Continue with other outputs?"):
                return 5

    # Compare with diff if requested
    if args.diff:
        compare_reports(report, Path(args.diff))

    # Sign artifacts
    should_sign = args.sign or not args.no_sign
    if should_sign and outputs:
        for output_path in outputs:
            try:
                signature = sign_artifact(output_path)
                console.print(f"[green]Signed[/green] {output_path} -> {signature}")
            except Exception as exc:
                console.print(f"[yellow]Failed to sign {output_path}:[/yellow] {exc}")

    # Log the audit activity
    try:
        append_encrypted_log({
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "user": getpass.getuser(),
            "repo": report.repo,
            "fingerprint": fingerprint,
            "artifacts": [str(path) for path in outputs],
            "violations": sum(len(f.violations) for f in report.files),
        })
    except Exception as exc:
        console.print(f"[yellow]Failed to write audit log:[/yellow] {exc}")

    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Main entry point with proper error handling."""
    try:
        return asyncio.run(run_cli(argv))
    except KeyboardInterrupt:
        console.print("[yellow]Scan interrupted by user[/yellow]")
        return 130
    except Exception as exc:
        console.print(f"[red]Unexpected error:[/red] {exc}")
        if __import__("os").getenv("DAT_DEBUG"):
            raise
        return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
