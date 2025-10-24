"""Repository scanning utilities."""
from __future__ import annotations

import asyncio
import fnmatch
import hashlib
import json
import mimetypes
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Sequence

from ..integration.lrc import extract_rules_from_schema, summarize_metadata
from ..rules.engine import Policy, Rule, RuleViolation, load_default_policy

try:  # pragma: no cover - optional dependency
    import magic  # type: ignore
except Exception:  # pragma: no cover - fallback when python-magic missing
    magic = None


@dataclass(slots=True)
class ScannerOptions:
    """Configuration for repository scanning."""

    root: Path
    ignore_patterns: Sequence[str] = field(default_factory=tuple)
    safe: bool = False
    deep: bool = False
    max_safe_size: int = 1_000_000
    semaphore: asyncio.Semaphore | None = None
    metadata: dict | None = None


@dataclass(slots=True)
class FileReport:
    """Structured information for a scanned file."""

    path: str
    size: int
    checksum: str
    mime_type: str
    encoding: str
    violations: List[RuleViolation]


@dataclass(slots=True)
class ScanReport:
    """Collection of file reports and summary metadata."""

    repo: str
    root: str
    files: List[FileReport]
    metadata: dict

    def to_dict(self) -> dict:
        return {
            "repo": self.repo,
            "root": self.root,
            "files": [
                {
                    "path": file.path,
                    "size": file.size,
                    "checksum": file.checksum,
                    "mime_type": file.mime_type,
                    "encoding": file.encoding,
                    "violations": [violation.__dict__ for violation in file.violations],
                }
                for file in self.files
            ],
            "metadata": self.metadata,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)


async def scan_repository(options: ScannerOptions, policy: Policy) -> ScanReport:
    """Scan *options.root* using *policy* and return a report."""

    files: List[FileReport] = []
    semaphore = options.semaphore or asyncio.Semaphore(32)

    async def process(path: Path) -> None:
        if should_ignore(path, options.ignore_patterns, options.root):
            return
        report = await analyse_file(path, options, policy, semaphore)
        if report:
            files.append(report)

    tasks: List[asyncio.Task[None]] = []
    for file_path in iter_files(options.root):
        tasks.append(asyncio.create_task(process(file_path)))
    if tasks:
        await asyncio.gather(*tasks)

    repo_name = options.root.name
    metadata = options.metadata or {}
    return ScanReport(repo=repo_name, root=str(options.root), files=sorted(files, key=lambda item: item.path), metadata=metadata)


def iter_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if path.is_file():
            yield path


def should_ignore(path: Path, patterns: Sequence[str], root: Path) -> bool:
    relative = str(path.relative_to(root))
    for pattern in patterns:
        if fnmatch.fnmatch(relative, pattern) or fnmatch.fnmatch(path.name, pattern):
            return True
    return False


async def analyse_file(path: Path, options: ScannerOptions, policy: Policy, semaphore: asyncio.Semaphore) -> FileReport | None:
    async with semaphore:
        stat = await asyncio.to_thread(path.stat)
        if options.safe and stat.st_size > options.max_safe_size:
            return None
        if not options.deep and path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".mp4"}:
            return None
        checksum = await asyncio.to_thread(hash_file, path)
        mime_type = detect_mime_type(path)
        content, encoding = await read_text_preview(path)
        if content is None:
            return FileReport(
                path=str(path),
                size=stat.st_size,
                checksum=checksum,
                mime_type=mime_type,
                encoding=encoding or "binary",
                violations=[],
            )
        violations = policy.evaluate(path=path, lines=content.splitlines())
        return FileReport(
            path=str(path),
            size=stat.st_size,
            checksum=checksum,
            mime_type=mime_type,
            encoding=encoding,
            violations=violations,
        )


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def detect_mime_type(path: Path) -> str:
    if magic:
        try:  # pragma: no branch - dependent on python-magic
            return magic.from_file(str(path), mime=True)  # type: ignore[arg-type]
        except Exception:
            pass
    mime_type, _ = mimetypes.guess_type(path.as_posix())
    return mime_type or "application/octet-stream"


async def read_text_preview(path: Path) -> tuple[str | None, str | None]:
    try:
        return await asyncio.to_thread(lambda: _read_text(path))
    except UnicodeDecodeError:
        return None, None


def _read_text(path: Path) -> tuple[str | None, str | None]:
    encodings = ["utf-8", "utf-16", "latin-1"]
    for encoding in encodings:
        try:
            text = path.read_text(encoding=encoding)
            return text, encoding
        except UnicodeDecodeError:
            continue
    return None, None


def build_policy_from_schema(schema_rules: Sequence[dict]) -> Policy:
    extra_rules: List[Rule] = []
    for entry in schema_rules:
        rule_id = entry.get("id")
        patterns = entry.get("patterns")
        if not rule_id or not patterns:
            continue
        if isinstance(patterns, str):
            patterns = [patterns]
        description = entry.get("description", rule_id)
        severity = entry.get("severity", "medium")
        extra_rules.append(
            Rule(rule_id=rule_id, description=description, patterns=tuple(patterns), severity=severity)
        )
    return load_default_policy(extra_rules)


async def build_scan_report(root: Path, *, ignore: Sequence[str], safe: bool, deep: bool, schema: dict | None) -> ScanReport:
    metadata = summarize_metadata(schema)
    options = ScannerOptions(root=root, ignore_patterns=ignore, safe=safe, deep=deep, metadata=metadata)
    schema_rules = extract_rules_from_schema(schema)
    policy = build_policy_from_schema(schema_rules)
    return await scan_repository(options, policy)
