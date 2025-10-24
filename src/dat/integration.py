"""LRC integration helpers."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable

from .report import serialise_findings, serialise_scan
from .rules import RuleFinding
from .scanner import ScanResult
from .utils import atomic_write, load_json, merge_dicts

LRC_CONFIG_PATH = Path.home() / ".config" / "lrc" / "dat_integration.json"


def load_lrc_config() -> Dict[str, Any]:
    """Load LRC integration configuration from the user's home directory."""

    return load_json(LRC_CONFIG_PATH)


def load_lrc_build(repo_root: Path) -> Dict[str, Any]:
    """Load `.lrc-build.json` from *repo_root* if present."""

    return load_json(repo_root / ".lrc-build.json")


def merge_lrc_metadata(config: Dict[str, Any], build: Dict[str, Any]) -> Dict[str, Any]:
    """Merge LRC config and build metadata."""

    return merge_dicts(config, build)


def write_lrc_audit(
    repo_root: Path, result: ScanResult, findings: Iterable[RuleFinding], metadata: dict
) -> Path:
    """Write `.lrc-audit.json` next to the build metadata."""

    output_path = repo_root / ".lrc-audit.json"
    payload = {
        "metadata": metadata,
        "scan": serialise_scan(result),
        "findings": serialise_findings(list(findings)),
    }
    atomic_write(output_path, json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2).encode("utf-8") + b"\n")
    return output_path
