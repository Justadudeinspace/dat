from __future__ import annotations

import asyncio
from pathlib import Path

from dat.scanner.core import build_scan_report


async def _scan(root: Path, **kwargs):
    return await build_scan_report(root, ignore=kwargs.get("ignore", []), safe=kwargs.get("safe", False), deep=kwargs.get("deep", False), schema=kwargs.get("schema"))


def test_scan_respects_ignore(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    (root / "keep.txt").write_text("hello", encoding="utf-8")
    (root / "skip.log").write_text("world", encoding="utf-8")
    report = asyncio.run(_scan(root, ignore=["*.log"]))
    files = [entry.path for entry in report.files]
    assert any("keep.txt" in path for path in files)
    assert all("skip.log" not in path for path in files)


def test_policy_from_schema(tmp_path: Path) -> None:
    schema_rules = [{"id": "custom", "patterns": ["ALERT"], "severity": "critical"}]
    root = tmp_path / "repo"
    root.mkdir()
    (root / "file.txt").write_text("ALERT", encoding="utf-8")
    report = asyncio.run(_scan(root, schema={"rules": schema_rules}))
    matches = [violation for file in report.files for violation in file.violations]
    assert any(violation.rule_id == "custom" for violation in matches)
