#!/usr/bin/env python3
"""
DAT (Dev Audit Tool) - Robust Simplified CLI
Enterprise security scanning with intuitive commands.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import List, Optional, Sequence

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from . import __version__
from .scanner.core import ScanReport, build_scan_report
from .integration.lrc import load_integration_config, select_schema
from .integration.signing import sign_artifact
from .logging.audit import append_encrypted_log
from .pdf.report import export_pdf

console = Console()


def build_parser() -> argparse.ArgumentParser:
    """
    Build simplified argument parser for DAT.
    Focus on intuitive commands and sensible defaults.
    """
    parser = argparse.ArgumentParser(
        description="DAT - Dev Audit Tool | Enterprise Security Scanning",
        epilog="""
📖 Examples:
  dat                          # Quick scan of current directory
  dat /path/to/project         # Scan specific project
  dat --deep                   # Deep scan (includes binaries)
  dat --pdf report.pdf         # Generate PDF report
  dat --ignore node_modules    # Exclude directories
  dat --sign                   # Sign reports with GPG
  dat --diff baseline.json     # Compare with previous scan

🎯 File Selection:
  dat -f src                   # Scan only src folder
  dat -s main.py               # Scan only main.py file  
  dat -a                       # Scan all files including hidden
  dat -f src -s main.py        # Combine folder and file filters

🔧 Advanced:
  dat --lrc                    # Enable compliance scanning
  dat --verbose                # Detailed output
  dat --json output.json       # JSON output for CI/CD
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Target selection
    target_group = parser.add_argument_group('📁 Scan Target')
    target_group.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Directory to scan (default: current directory)'
    )

    # File selection options
    selection_group = parser.add_argument_group('🎯 File Selection')
    selection_group.add_argument(
        '-f', '--folder',
        help='Scan only the specified folder (relative to target)'
    )
    selection_group.add_argument(
        '-s', '--single-file',
        help='Scan only the specified file (relative to target)'
    )
    selection_group.add_argument(
        '-a', '--all',
        action='store_true',
        help='Scan all files including hidden files'
    )

    # Scan mode
    mode_group = parser.add_argument_group('🔍 Scan Mode')
    mode_group.add_argument(
        '-d', '--deep',
        action='store_true',
        help='Deep scan (include binary files, no size limits)'
    )
    mode_group.add_argument(
        '--fast',
        action='store_true',
        help='Fast scan (skip large files, basic analysis)'
    )
    mode_group.add_argument(
        '--audit',
        action='store_true',
        help='Compliance audit mode (strict rules, detailed reporting)'
    )

    # Output options
    output_group = parser.add_argument_group('📊 Output Options')
    output_group.add_argument(
        '-o', '--output',
        help='Output file (auto-detects format from extension)'
    )
    output_group.add_argument(
        '--json',
        help='Save as JSON report'
    )
    output_group.add_argument(
        '--pdf',
        help='Save as PDF report'
    )
    output_group.add_argument(
        '--md', '--markdown',
        help='Save as Markdown report'
    )

    # Filtering
    filter_group = parser.add_argument_group('🎯 Filtering')
    filter_group.add_argument(
        '-i', '--ignore',
        action='append',
        default=[],
        help='Ignore pattern (e.g., node_modules, *.log)'
    )
    filter_group.add_argument(
        '--only',
        action='append',
        default=[],
        help='Only scan specific patterns (e.g., *.py, src/**)'
    )

    # Enterprise features
    enterprise_group = parser.add_argument_group('🏢 Enterprise Features')
    enterprise_group.add_argument(
        '--lrc',
        action='store_true',
        help='Enable LRC compliance integration'
    )
    enterprise_group.add_argument(
        '--sign',
        action='store_true',
        help='Sign reports with GPG'
    )
    enterprise_group.add_argument(
        '--diff',
        help='Compare with previous scan report'
    )

    # Information & debugging
    info_group = parser.add_argument_group('ℹ️  Information')
    info_group.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output with detailed information'
    )
    info_group.add_argument(
        '--version',
        action='store_true',
        help='Show version information and exit'
    )
    info_group.add_argument(
        '--stats',
        action='store_true',
        help='Show detailed statistics after scan'
    )

    return parser


def display_banner() -> None:
    """Display DAT banner with version information."""
    banner = Text()
    banner.append("DAT ", style="bold cyan")
    banner.append("Dev Audit Tool", style="bold white")
    banner.append(f" v{__version__}", style="bold green")
    banner.append("\nEnterprise Security & Compliance Scanning", style="dim")

    console.print(Panel(banner, style="cyan", padding=(1, 2)))


def display_quick_help() -> None:
    """Display quick help reference."""
    help_table = Table(show_header=False, box=None, padding=(0, 2))
    help_table.add_column("Command", style="cyan")
    help_table.add_column("Description", style="white")

    help_table.add_row("dat [path]", "Quick scan of directory")
    help_table.add_row("dat --deep", "Deep scan (includes binaries)")
    help_table.add_row("dat --pdf report.pdf", "Generate PDF report")
    help_table.add_row("dat --ignore node_modules", "Exclude directories")
    help_table.add_row("dat -f src", "Scan only src folder")
    help_table.add_row("dat -s main.py", "Scan only main.py file")
    help_table.add_row("dat -a", "Scan all files including hidden")
    help_table.add_row("dat --lrc --sign", "Compliance scan with signing")
    help_table.add_row("dat --diff baseline.json", "Compare with previous scan")

    console.print(Panel(help_table, title="🚀 Quick Start", style="green"))


def validate_args(args: argparse.Namespace) -> tuple[bool, str]:
    """
    Validate command line arguments.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check path exists
    target_path = Path(args.path)
    if not target_path.exists():
        return False, f"Target path does not exist: {args.path}"
    
    if not target_path.is_dir():
        return False, f"Target path is not a directory: {args.path}"

    # Check folder selection exists
    if args.folder:
        folder_path = target_path / args.folder
        if not folder_path.exists():
            return False, f"Selected folder does not exist: {args.folder}"
        if not folder_path.is_dir():
            return False, f"Selected folder is not a directory: {args.folder}"

    # Check single file selection exists
    if args.single_file:
        file_path = target_path / args.single_file
        if not file_path.exists():
            return False, f"Selected file does not exist: {args.single_file}"
        if not file_path.is_file():
            return False, f"Selected file is not a file: {args.single_file}"

    # Check for conflicting output options
    output_files = [args.output, args.json, args.pdf, args.md]
    output_files = [f for f in output_files if f is not None]
    
    if len(output_files) > 1:
        return False, "Specify only one output format at a time"

    # Check diff file exists if provided
    if args.diff and not Path(args.diff).exists():
        return False, f"Diff baseline file not found: {args.diff}"

    return True, ""


def determine_scan_mode(args: argparse.Namespace) -> dict:
    """
    Determine scan parameters based on mode flags.
    
    Returns:
        Dictionary of scan parameters
    """
    if args.deep:
        return {
            'safe': False,
            'deep': True,
            'max_size': None,
            'max_lines': None
        }
    elif args.fast:
        return {
            'safe': True,
            'deep': False,
            'max_size': 5 * 1024 * 1024,  # 5MB
            'max_lines': 500
        }
    elif args.audit:
        return {
            'safe': False,
            'deep': True,
            'max_size': None,
            'max_lines': None
        }
    else:
        # Default balanced mode
        return {
            'safe': True,
            'deep': False,
            'max_size': 10 * 1024 * 1024,  # 10MB
            'max_lines': 1000
        }


def build_custom_ignore_patterns(args: argparse.Namespace, target: Path) -> List[str]:
    """
    Build custom ignore patterns based on file selection arguments.
    
    Returns:
        List of ignore patterns
    """
    ignore_patterns = list(args.ignore or [])
    
    # If specific folder is selected, ignore everything else
    if args.folder:
        # Convert folder to pattern that ignores everything not in the selected folder
        folder_pattern = args.folder.rstrip('/')
        # Ignore all files not starting with the folder path
        ignore_patterns.append(f"!{folder_pattern}/**")  # Negative pattern to keep
        ignore_patterns.append("**")  # Then ignore everything else
    
    # If single file is selected, ignore everything else
    elif args.single_file:
        file_pattern = args.single_file
        # Keep only the specific file, ignore everything else
        ignore_patterns.append(f"!{file_pattern}")  # Negative pattern to keep
        ignore_patterns.append("**")  # Then ignore everything else
    
    # If --all is not specified, ignore hidden files by default
    if not args.all:
        ignore_patterns.extend([
            ".*",           # Hidden files
            "*/.*",         # Hidden files in subdirectories
            ".*/**",        # Hidden directories
        ])
    
    return ignore_patterns


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def display_scan_progress(target: Path, mode: str, args: argparse.Namespace) -> None:
    """Display scan progress information."""
    mode_descriptions = {
        'deep': '🔍 Deep Scan (all files, no limits)',
        'fast': '⚡ Fast Scan (skip large files)',
        'audit': '🏢 Compliance Audit (strict rules)',
        'default': '✅ Standard Scan (safe defaults)'
    }
    
    console.print(f"\n[bold]Target:[/bold] {target}")
    
    # Show file selection info
    selection_info = []
    if args.folder:
        selection_info.append(f"Folder: {args.folder}")
    if args.single_file:
        selection_info.append(f"File: {args.single_file}")
    if args.all:
        selection_info.append("All files (including hidden)")
    
    if selection_info:
        console.print(f"[bold]Selection:[/bold] {', '.join(selection_info)}")
    
    console.print(f"[bold]Mode:[/bold] {mode_descriptions.get(mode, mode_descriptions['default'])}")
    console.print("Scanning...", end="")


def display_scan_summary(report: ScanReport, args: argparse.Namespace) -> None:
    """Display comprehensive scan summary."""
    verbose = args.verbose or args.stats
    
    # Main summary table
    summary_table = Table(title="📊 Scan Summary", show_header=True, header_style="bold magenta")
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value", style="white")
    summary_table.add_column("Status", style="green")

    total_files = report.total_files
    total_violations = report.total_violations
    critical_violations = sum(1 for f in report.files for v in f.violations if v.severity == 'critical')
    high_violations = sum(1 for f in report.files for v in f.violations if v.severity == 'high')

    summary_table.add_row("Files Scanned", str(total_files), "✅" if total_files > 0 else "⚠️")
    summary_table.add_row("Total Violations", str(total_violations), 
                         "✅" if total_violations == 0 else "❌")
    summary_table.add_row("Critical", str(critical_violations),
                         "✅" if critical_violations == 0 else "🔴")
    summary_table.add_row("High", str(high_violations),
                         "✅" if high_violations == 0 else "🟡")

    console.print(summary_table)

    # Show selected files if single file or small folder scan
    if args.single_file or (args.folder and total_files <= 20):
        files_table = Table(title="📁 Scanned Files", show_header=True, header_style="bold blue")
        files_table.add_column("File", style="cyan")
        files_table.add_column("Size", style="white")
        files_table.add_column("Violations", style="red")
        
        for file_report in report.files:
            violation_count = len(file_report.violations)
            files_table.add_row(
                file_report.path,
                format_file_size(file_report.size),
                str(violation_count) if violation_count > 0 else "0"
            )
        
        console.print(files_table)

    # File type breakdown if verbose
    if verbose and report.files:
        file_types = {}
        for file_report in report.files:
            ext = Path(file_report.path).suffix.lower() or 'no extension'
            file_types[ext] = file_types.get(ext, 0) + 1
        
        if file_types:
            type_table = Table(title="📁 File Types", show_header=True, header_style="bold blue")
            type_table.add_column("Extension", style="cyan")
            type_table.add_column("Count", style="white")
            
            for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:10]:
                type_table.add_row(ext, str(count))
            
            console.print(type_table)

    # Top violations if any
    if total_violations > 0:
        violations_table = Table(title="🚨 Top Violations", show_header=True, header_style="bold red")
        violations_table.add_column("File", style="cyan")
        violations_table.add_column("Rule", style="yellow")
        violations_table.add_column("Severity", style="red")
        violations_table.add_column("Message", style="white")

        violation_count = 0
        for file_report in report.files:
            for violation in file_report.violations:
                if violation_count < 10:  # Show top 10
                    severity_emoji = {
                        'critical': '🔴',
                        'high': '🟡', 
                        'medium': '🟠',
                        'low': '🔵',
                        'info': '⚪'
                    }.get(violation.severity, '⚪')
                    
                    violations_table.add_row(
                        file_report.path,
                        violation.rule_id,
                        f"{severity_emoji} {violation.severity}",
                        violation.message[:50] + "..." if len(violation.message) > 50 else violation.message
                    )
                    violation_count += 1

        console.print(violations_table)


def write_report_file(report: ScanReport, file_path: str, format_type: str) -> Path:
    """Write report in specified format."""
    path = Path(file_path)
    fingerprint = __import__("hashlib").sha256(report.to_json().encode("utf-8")).hexdigest()

    if format_type == 'json':
        from .integration.signing import getpass
        from datetime import datetime
        
        payload = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "user": getpass.getuser(),
            "repo": report.repo,
            "fingerprint": fingerprint,
            "report": report.to_dict(),
        }
        
        path.write_text(json.dumps(payload, indent=2), encoding='utf-8')
        console.print(f"[green]✓ JSON report saved:[/green] {path}")
        
    elif format_type == 'pdf':
        export_pdf(report, path)
        console.print(f"[green]✓ PDF report saved:[/green] {path}")
        
    elif format_type == 'markdown':
        # Simple markdown report
        lines = [
            f"# DAT Scan Report - {report.repo}",
            f"**Generated:** {datetime.utcnow().isoformat()}Z",
            f"**Files:** {report.total_files}",
            f"**Violations:** {report.total_violations}",
            "",
            "## Files Scanned",
        ]
        
        for file_report in report.files[:50]:  # Limit to first 50 files
            lines.append(f"- {file_report.path} ({format_file_size(file_report.size)})")
            for violation in file_report.violations:
                lines.append(f"  - [{violation.severity.upper()}] {violation.rule_id}: {violation.message}")
        
        path.write_text('\n'.join(lines), encoding='utf-8')
        console.print(f"[green]✓ Markdown report saved:[/green] {path}")

    return path


async def run_scan(args: argparse.Namespace) -> tuple[ScanReport, int]:
    """Execute the scan with given arguments."""
    target = Path(args.path).resolve()
    
    # Determine scan mode
    scan_params = determine_scan_mode(args)
    mode_name = 'deep' if args.deep else 'fast' if args.fast else 'audit' if args.audit else 'default'
    
    display_scan_progress(target, mode_name, args)
    
    # Build custom ignore patterns based on file selection
    ignore_patterns = build_custom_ignore_patterns(args, target)
    
    # Load LRC schema if requested
    schema = None
    if args.lrc:
        try:
            config = load_integration_config()
            schema = select_schema(config, target.name)
            console.print("\n[blue]✓ LRC compliance rules enabled[/blue]")
        except Exception as e:
            console.print(f"\n[yellow]⚠ LRC config error: {e}[/yellow]")

    # Build scan report
    try:
        report = await build_scan_report(
            target,
            ignore=ignore_patterns,
            safe=scan_params['safe'],
            deep=scan_params['deep'],
            schema=schema
        )
        console.print(" [green]✓[/green]")
        
    except Exception as e:
        console.print(f" [red]✗[/red]")
        console.print(f"[red]Scan failed: {e}[/red]")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return None, 1

    return report, 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    """
    Main CLI entry point with simplified interface.
    
    Returns:
        Exit code (0 = success, 1 = error, 3 = violations found)
    """
    try:
        parser = build_parser()
        args = parser.parse_args(argv)

        # Handle version flag
        if args.version:
            print(f"DAT v{__version__}")
            return 0

        # Display banner (except for machine-readable output)
        if not any([args.json, args.pdf, args.md]):
            display_banner()
            
            # Show quick help if no arguments beyond path
            if len(sys.argv) == 2 and sys.argv[1] in ['.', '', args.path]:
                display_quick_help()

        # Validate arguments
        is_valid, error_msg = validate_args(args)
        if not is_valid:
            console.print(f"[red]Error: {error_msg}[/red]")
            return 1

        # Run the scan
        report, exit_code = asyncio.run(run_scan(args))
        if exit_code != 0:
            return exit_code

        # Display results
        display_scan_summary(report, args)

        # Handle output files
        outputs = []
        if args.output:
            # Auto-detect format from extension
            ext = Path(args.output).suffix.lower()
            if ext == '.json':
                outputs.append(write_report_file(report, args.output, 'json'))
            elif ext == '.pdf':
                outputs.append(write_report_file(report, args.output, 'pdf'))
            elif ext in ['.md', '.markdown']:
                outputs.append(write_report_file(report, args.output, 'markdown'))
            else:
                # Default to JSON
                outputs.append(write_report_file(report, args.output, 'json'))
                
        elif args.json:
            outputs.append(write_report_file(report, args.json, 'json'))
        elif args.pdf:
            outputs.append(write_report_file(report, args.pdf, 'pdf'))
        elif args.md:
            outputs.append(write_report_file(report, args.md, 'markdown'))
        else:
            # Default: create JSONL in current directory
            default_output = Path(report.repo or 'scan') / "dat-report.jsonl"
            default_output.parent.mkdir(exist_ok=True)
            outputs.append(write_report_file(report, str(default_output), 'json'))

        # Sign artifacts if requested
        if args.sign and outputs:
            for output_path in outputs:
                try:
                    signature = sign_artifact(output_path)
                    console.print(f"[green]✓ Signed:[/green] {signature}")
                except Exception as e:
                    console.print(f"[yellow]⚠ Signing failed: {e}[/yellow]")

        # Handle diff comparison
        if args.diff:
            from .scanner.core import ScanReport as SR
            try:
                previous_data = json.loads(Path(args.diff).read_text())
                previous_report = SR.from_dict(previous_data.get('report', {}))
                
                current_violations = report.total_violations
                previous_violations = previous_report.total_violations
                
                if current_violations > previous_violations:
                    console.print(f"[red]❌ Regressions detected: {previous_violations} → {current_violations} violations[/red]")
                    return 3
                elif current_violations < previous_violations:
                    console.print(f"[green]✓ Improvements: {previous_violations} → {current_violations} violations[/green]")
                else:
                    console.print(f"[green]✓ No change: {current_violations} violations[/green]")
                    
            except Exception as e:
                console.print(f"[yellow]⚠ Diff comparison failed: {e}[/yellow]")

        # Log audit entry
        try:
            selection_type = "single_file" if args.single_file else "folder" if args.folder else "all" if args.all else "standard"
            append_encrypted_log({
                "timestamp": __import__("datetime").datetime.utcnow().isoformat() + "Z",
                "user": __import__("getpass").getuser(),
                "repo": report.repo,
                "files": report.total_files,
                "violations": report.total_violations,
                "selection": selection_type,
                "mode": "deep" if args.deep else "fast" if args.fast else "audit" if args.audit else "standard"
            })
        except Exception as e:
            if args.verbose:
                console.print(f"[yellow]⚠ Audit logging failed: {e}[/yellow]")

        # Return appropriate exit code based on violations
        if report.total_violations > 0:
            console.print(f"\n[yellow]⚠ Scan completed with {report.total_violations} violations[/yellow]")
            return 3
        else:
            console.print(f"\n[green]✓ Scan completed successfully - no violations found[/green]")
            return 0

    except KeyboardInterrupt:
        console.print("\n[yellow]⚠ Scan interrupted by user[/yellow]")
        return 130
    except Exception as e:
        console.print(f"[red]💥 Unexpected error: {e}[/red]")
        if __import__("os").getenv("DAT_DEBUG"):
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
