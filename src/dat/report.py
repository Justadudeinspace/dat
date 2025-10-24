"""Report generation utilities."""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List

from . import __version__
from .rules import RuleFinding
from .scanner import ScanResult
from .utils import atomic_write


def build_metadata(root: Path, *, lrc: dict | None = None) -> Dict[str, Any]:
    """Construct metadata shared across report types."""

    now = dt.datetime.now(dt.timezone.utc)
    metadata: Dict[str, Any] = {
        "dat_version": __version__,
        "generated_at": now.isoformat(),
        "root": str(root),
    }
    if lrc:
        metadata["lrc"] = lrc
    return metadata


def serialise_scan(result: ScanResult) -> Dict[str, Any]:
    """Serialise :class:`ScanResult` into JSON ready structure."""

    return {
        "root": str(result.root),
        "stats": {
            "scanned": result.stats.scanned,
            "skipped": result.stats.skipped,
            "binary": result.stats.binary,
            "errors": result.stats.errors,
        },
        "files": [
            {
                "path": record.path,
                "size": record.size,
                "lines": record.lines,
                "binary": record.binary,
            }
            for record in result.files
        ],
        "skipped": result.skipped,
        "errors": result.errors,
    }


def serialise_findings(findings: Iterable[RuleFinding]) -> List[Dict[str, Any]]:
    """Serialise policy findings."""

    return [
        {
            "rule_id": finding.rule_id,
            "message": finding.message,
            "severity": finding.severity,
            "path": finding.path,
        }
        for finding in findings
    ]


def write_json_report(path: Path, result: ScanResult, findings: Iterable[RuleFinding], metadata: dict) -> Path:
    """Write a JSON report combining scan results and metadata."""

    findings_list = list(findings)
    report = {
        "metadata": metadata,
        "scan": serialise_scan(result),
        "findings": serialise_findings(findings_list),
    }
    payload = json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2).encode("utf-8") + b"\n"
    atomic_write(path, payload)
    return path


def write_markdown_report(path: Path, result: ScanResult, findings: Iterable[RuleFinding], metadata: dict) -> Path:
    """Persist a Markdown summary of the scan."""

    findings_list = list(findings)
    lines: List[str] = []
    lines.append(f"# DAT Audit Report")
    lines.append("")
    lines.append(f"- **Version**: {metadata.get('dat_version', __version__)}")
    lines.append(f"- **Generated**: {metadata.get('generated_at', '')}")
    if lrc := metadata.get("lrc"):
        lines.append("- **LRC Project**: {project}".format(project=lrc.get("project", "unknown")))
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(
        f"Scanned {result.stats.scanned} files with {result.stats.binary} binary files and {len(result.errors)} errors."
    )
    if result.skipped:
        lines.append("")
        lines.append("### Skipped Files")
        for item in result.skipped[:20]:
            lines.append(f"- {item}")
        if len(result.skipped) > 20:
            lines.append(f"- ... {len(result.skipped) - 20} more")
    if findings_list:
        lines.append("")
        lines.append("## Findings")
        for finding in findings_list:
            location = f" ({finding.path})" if finding.path else ""
            lines.append(f"- **{finding.severity.upper()}** [{finding.rule_id}]{location}: {finding.message}")
    payload = "\n".join(lines).encode("utf-8") + b"\n"
    atomic_write(path, payload)
    return path
