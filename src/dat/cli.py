"""Command line interface for the Dev Audit Tool."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Sequence

from . import __version__
from .integration import load_lrc_build, load_lrc_config, merge_lrc_metadata, write_lrc_audit
from .pdf import write_pdf_report
from .report import build_metadata, serialise_scan, write_json_report, write_markdown_report
from .rules import evaluate_rules
from .scanner import scan_repository
from .utils import TERMINAL_STYLE, color_text, iter_ignore_patterns, run_gpg_sign


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Dev Audit Tool")
    parser.add_argument("path", nargs="?", default=".", help="Repository path to scan")
    parser.add_argument("--from-lrc", action="store_true", help="Load LRC metadata for the scan")
    parser.add_argument("-i", "--ignore", action="append", default=[], help="Glob pattern to ignore")
    parser.add_argument("--max-lines", type=int, default=1000, help="Maximum lines per file in safe mode")
    parser.add_argument("--max-size", type=int, default=10 * 1024 * 1024, help="Maximum file size in safe mode")
    parser.add_argument("--safe", dest="safe", action="store_true", help="Enable safe scanning (default)")
    parser.add_argument("--no-safe", dest="safe", action="store_false", help="Disable safe scanning")
    parser.set_defaults(safe=True)
    parser.add_argument("--deep", action="store_true", help="Perform a deep scan (overrides safe limits)")
    parser.add_argument("--report", type=str, help="Path to JSON or Markdown report")
    parser.add_argument("-o", "--output", type=str, help="Path to PDF report")
    parser.add_argument("--sign", action="store_true", help="Sign generated reports with GPG")
    parser.add_argument("--diff", type=str, help="Compare against a previous JSON report")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose console output")
    parser.add_argument("--version", action="store_true", help="Display version information")
    return parser


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.version:
        print(__version__)
        raise SystemExit(0)
    return args


def normalise_path(path: str) -> Path:
    return Path(path).expanduser().resolve()


def determine_safe_mode(args: argparse.Namespace) -> bool:
    if args.deep:
        return False
    return bool(args.safe)


def main(argv: Sequence[str] | None = None) -> int:
    try:
        args = parse_args(argv)
    except SystemExit as exc:
        return exc.code

    root = normalise_path(args.path)
    if not root.exists():
        print(color_text(f"Path does not exist: {root}", TERMINAL_STYLE.error), file=sys.stderr)
        return 1

    ignore_patterns = list(iter_ignore_patterns(args.ignore))
    safe_mode = determine_safe_mode(args)

    result = scan_repository(
        root,
        ignore_patterns,
        max_lines=args.max_lines,
        max_size=args.max_size,
        safe=safe_mode,
        deep=args.deep,
    )

    findings = list(evaluate_rules(result.root, result.files))

    lrc_metadata = None
    if args.from_lrc:
        config = load_lrc_config()
        build = load_lrc_build(result.root)
        lrc_metadata = merge_lrc_metadata(config, build)

    metadata = build_metadata(result.root, lrc=lrc_metadata)

    outputs: List[Path] = []

    if args.report:
        report_path = normalise_path(args.report)
        suffix = report_path.suffix.lower()
        if suffix == ".json":
            outputs.append(write_json_report(report_path, result, findings, metadata))
        elif suffix in {".md", ".markdown"}:
            outputs.append(write_markdown_report(report_path, result, findings, metadata))
        else:
            print(color_text("Unsupported report extension", TERMINAL_STYLE.error), file=sys.stderr)
            return 2

    if args.output:
        pdf_path = normalise_path(args.output)
        outputs.append(write_pdf_report(pdf_path, result, findings, metadata))

    if args.from_lrc:
        outputs.append(write_lrc_audit(result.root, result, findings, metadata))

    if args.diff:
        diff_path = normalise_path(args.diff)
        try:
            previous = json.loads(diff_path.read_text(encoding="utf-8"))
        except Exception as exc:  # pragma: no cover - diff errors
            print(color_text(f"Unable to load diff baseline: {exc}", TERMINAL_STYLE.error), file=sys.stderr)
            return 3
        current = {"scan": serialise_scan(result)}
        if previous.get("scan") != current.get("scan"):
            print(color_text("Differences detected compared to baseline", TERMINAL_STYLE.warning))
        else:
            print(color_text("No differences detected", TERMINAL_STYLE.success))

    if args.sign:
        for path in outputs:
            signature = path.with_suffix(path.suffix + ".asc")
            if not run_gpg_sign(path, signature):
                print(color_text(f"Failed to sign {path}", TERMINAL_STYLE.warning), file=sys.stderr)

    if args.verbose:
        print(color_text(f"Scanned {result.stats.scanned} files", TERMINAL_STYLE.success))
        if result.skipped:
            print(color_text(f"Skipped {len(result.skipped)} files", TERMINAL_STYLE.warning))
        if result.errors:
            print(color_text(f"Encountered {len(result.errors)} errors", TERMINAL_STYLE.error))

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
