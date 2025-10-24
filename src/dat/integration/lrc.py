"""Integration helpers for LRC generated metadata."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List

LRC_CONFIG_PATH = Path(os.environ.get("LRC_CONFIG_PATH", Path.home() / ".config" / "lrc" / "dat_integration.json"))


class LRCIntegrationError(RuntimeError):
    """Raised when LRC integration fails."""


def load_integration_config(path: Path | None = None) -> Dict[str, Any]:
    """Load the LRC integration configuration file."""

    config_path = Path(path or LRC_CONFIG_PATH)
    if not config_path.exists():
        return {}
    try:
        return json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:  # pragma: no cover - invalid files are rare
        raise LRCIntegrationError(f"Invalid LRC integration config: {config_path}") from exc


def select_schema(config: Dict[str, Any], repo_name: str | None) -> Dict[str, Any] | None:
    """Select the schema entry matching *repo_name*."""

    schemas: Iterable[Dict[str, Any]] = config.get("schemas", [])  # type: ignore[assignment]
    for schema in schemas:
        targets: List[str] = schema.get("repos", [])  # type: ignore[assignment]
        if not targets or (repo_name and repo_name in targets):
            return schema
    return None


def extract_rules_from_schema(schema: Dict[str, Any] | None) -> List[Dict[str, Any]]:
    """Return policy rules defined inside *schema*."""

    if not schema:
        return []
    rules = schema.get("rules")
    if isinstance(rules, list):
        return [rule for rule in rules if isinstance(rule, dict)]
    return []


def summarize_metadata(schema: Dict[str, Any] | None) -> Dict[str, Any]:
    """Return the metadata subset relevant for audit reports."""

    if not schema:
        return {}
    allowed_keys = {"owner", "repository", "compliance", "notes"}
    return {key: value for key, value in schema.items() if key in allowed_keys}
