"""Policy evaluation hooks for DAT."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

from .scanner import FileRecord


@dataclass
class RuleFinding:
    """Represents a policy finding generated during scans."""

    rule_id: str
    message: str
    severity: str
    path: str | None = None


DEFAULT_RULES = (
    ("no.todo", "TODO comment detected", "low"),
    ("no.merge", "Potential merge conflict marker", "medium"),
)

RULE_LOOKUP = {rule_id: (message, severity) for rule_id, message, severity in DEFAULT_RULES}


def evaluate_rules(root: Path, files: Iterable[FileRecord]) -> List[RuleFinding]:
    """Evaluate :data:`DEFAULT_RULES` against scanned *files* within *root*."""

    findings: List[RuleFinding] = []
    for record in files:
        if record.binary:
            continue
        if record.path.endswith(".md"):
            continue
        # simple heuristics using file content
        try:
            text = (root / record.path).read_text(encoding="utf-8")
        except Exception:
            continue
        if "TODO" in text and "no.todo" in RULE_LOOKUP:
            message, severity = RULE_LOOKUP["no.todo"]
            findings.append(RuleFinding("no.todo", message, severity, record.path))
        if ("<<<<" in text or ">>>>" in text) and "no.merge" in RULE_LOOKUP:
            message, severity = RULE_LOOKUP["no.merge"]
            findings.append(RuleFinding("no.merge", message, severity, record.path))
    return findings
