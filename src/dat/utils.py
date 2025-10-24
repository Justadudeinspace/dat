"""Utility helpers for the Dev Audit Tool."""
from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import tempfile
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Sequence

from colorama import Fore, Style, init as colorama_init

try:  # pragma: no cover - python-magic is optional on Windows
    import magic  # type: ignore
except Exception:  # pragma: no cover
    magic = None  # type: ignore

DEFAULT_ENCODING = "utf-8"
ENCODING_FALLBACKS = ("utf-8", "utf-8-sig", "latin-1", "utf-16")

colorama_init(strip=False, convert=False, autoreset=True)


@dataclass(frozen=True)
class TerminalStyle:
    """Reusable terminal style snippets."""

    success: str = Fore.GREEN
    warning: str = Fore.YELLOW
    error: str = Fore.RED
    reset: str = Style.RESET_ALL


TERMINAL_STYLE = TerminalStyle()


def detect_encoding(path: Path) -> str:
    """Best-effort encoding detection for *path*."""

    for encoding in ENCODING_FALLBACKS:
        try:
            path.read_text(encoding=encoding)
            return encoding
        except UnicodeDecodeError:
            continue
        except OSError:
            break
    return DEFAULT_ENCODING


def read_text(path: Path) -> str:
    """Load text content handling binary files gracefully."""

    for encoding in ENCODING_FALLBACKS:
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    # Fallback to latin-1 to preserve bytes
    with path.open("r", encoding="latin-1", errors="ignore") as handle:
        return handle.read()


def is_binary(path: Path) -> bool:
    """Return True if the file is binary."""

    if magic is not None:
        with suppress(Exception):
            mime = magic.from_file(str(path), mime=True)  # type: ignore[attr-defined]
            if mime:
                return not mime.startswith("text/")
    with suppress(OSError):
        chunk = path.read_bytes()[:1024]
        if b"\0" in chunk:
            return True
    return False


def terminal_width(default: int = 80) -> int:
    """Return the terminal width or *default* when unavailable."""

    with suppress(OSError):
        return shutil.get_terminal_size((default, 20)).columns
    return default


def color_text(text: str, colour: str | None) -> str:
    """Wrap *text* with the provided colour, resetting afterwards."""

    if not colour:
        return text
    return f"{colour}{text}{TERMINAL_STYLE.reset}"


def iter_ignore_patterns(patterns: Sequence[str]) -> Iterator[str]:
    """Yield ignore patterns while filtering empty values."""

    for pattern in patterns:
        if pattern:
            yield pattern


def atomic_write(path: Path, data: bytes) -> None:
    """Atomically persist *data* to *path*."""

    target = path.resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(delete=False, dir=str(target.parent)) as handle:
        handle.write(data)
        temp_name = Path(handle.name)
    temp_name.chmod(stat.S_IRUSR | stat.S_IWUSR)
    os.replace(temp_name, target)


def run_gpg_sign(data_path: Path, output_path: Path) -> bool:
    """Attempt to sign *data_path* using gpg, writing to *output_path*."""

    command = ["gpg", "--armor", "--output", str(output_path), "--detach-sign", str(data_path)]
    try:
        completed = subprocess.run(command, check=False, capture_output=True, text=True)
    except FileNotFoundError:
        return False
    if completed.returncode != 0:
        return False
    return output_path.exists()


def load_json(path: Path) -> dict:
    """Load JSON content from *path* returning an empty dict on failure."""

    with suppress(OSError, json.JSONDecodeError):
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def merge_dicts(base: dict, override: dict) -> dict:
    """Deep merge dictionaries with override precedence."""

    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    return result


def ensure_home_config(path: Path) -> None:
    """Ensure *path* exists with secure permissions."""

    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("[]", encoding="utf-8")
        path.chmod(stat.S_IRUSR | stat.S_IWUSR)
