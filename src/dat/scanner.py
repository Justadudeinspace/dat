"""Repository scanning primitives."""
from __future__ import annotations

import fnmatch
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List

from .utils import is_binary


@dataclass
class FileRecord:
    """Metadata describing a scanned file."""

    path: str
    size: int
    lines: int
    binary: bool


@dataclass
class ScanStatistics:
    """Collection of scan statistics."""

    scanned: int = 0
    skipped: int = 0
    binary: int = 0
    errors: int = 0


@dataclass
class ScanResult:
    """Return value from :func:`scan_repository`."""

    root: Path
    files: List[FileRecord] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    stats: ScanStatistics = field(default_factory=ScanStatistics)


def should_ignore(path: Path, patterns: Iterable[str]) -> bool:
    """Return True when *path* matches any ignore pattern."""

    return any(fnmatch.fnmatch(path.name, pattern) or fnmatch.fnmatch(str(path), pattern) for pattern in patterns)


def count_lines(path: Path, binary: bool, max_lines: int | None) -> int:
    """Count the lines in *path* respecting *max_lines*."""

    if binary:
        return 0
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            line_count = 0
            for line_count, _line in enumerate(handle, start=1):
                if max_lines and line_count > max_lines:
                    return line_count
            return line_count
    except OSError:
        return 0


def scan_repository(
    root: Path,
    ignore_patterns: Iterable[str] | None = None,
    *,
    max_lines: int = 1000,
    max_size: int = 10 * 1024 * 1024,
    safe: bool = True,
    deep: bool = False,
) -> ScanResult:
    """Walk *root* and capture metadata respecting ignore patterns and thresholds."""

    result = ScanResult(root=root.resolve())
    ignore_patterns = list(ignore_patterns or [])

    for dirpath, dirnames, filenames in os.walk(result.root):
        current = Path(dirpath)
        # Filter ignored directories
        dirnames[:] = [d for d in dirnames if not should_ignore(current / d, ignore_patterns)]

        for name in filenames:
            file_path = current / name
            if should_ignore(file_path, ignore_patterns):
                result.stats.skipped += 1
                result.skipped.append(str(file_path.relative_to(result.root)))
                continue

            try:
                size = file_path.stat().st_size
            except OSError as exc:  # pragma: no cover - race conditions
                result.errors.append(f"{file_path}: {exc}")
                result.stats.errors += 1
                continue

            binary = is_binary(file_path)
            if binary:
                result.stats.binary += 1

            if safe and binary:
                result.stats.skipped += 1
                result.skipped.append(str(file_path.relative_to(result.root)))
                continue

            if safe and size > max_size:
                result.stats.skipped += 1
                result.skipped.append(str(file_path.relative_to(result.root)))
                continue

            lines = count_lines(file_path, binary, None if deep else max_lines)
            if safe and not deep and lines > max_lines:
                result.stats.skipped += 1
                result.skipped.append(str(file_path.relative_to(result.root)))
                continue

            record = FileRecord(
                path=str(file_path.relative_to(result.root)),
                size=size,
                lines=lines,
                binary=binary,
            )
            result.files.append(record)
            result.stats.scanned += 1

    result.files.sort(key=lambda record: record.path)
    result.skipped.sort()
    result.errors.sort()
    return result
