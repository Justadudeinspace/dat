"""Dev Audit Tool (DAT) public package interface."""
from __future__ import annotations

from pathlib import Path

__all__ = ["__version__", "get_version", "repository_root"]

__version__ = "3.0.0-alpha.1"


def get_version() -> str:
    """Return the DAT package version."""

    return __version__


def repository_root(start: Path | None = None) -> Path:
    """Locate the repository root starting from *start* or the current working directory."""

    current = Path(start or Path.cwd()).resolve()
    for parent in (current, *current.parents):
        if (parent / ".git").exists():
            return parent
    return current


# Backwards compatible CLI access
from .cli import main  # noqa: E402,F401

__all__.append("main")
