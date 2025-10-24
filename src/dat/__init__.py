"""Dev Audit Tool (DAT) enterprise package."""
from __future__ import annotations

from importlib import metadata
from pathlib import Path

__all__ = [
    "__version__",
    "get_version",
    "repository_root",
]

try:
    __version__ = metadata.version("dat")
except metadata.PackageNotFoundError:  # pragma: no cover - fallback for local dev
    __version__ = "3.0.0-alpha.1"


def get_version() -> str:
    """Return the human friendly version string."""
    return __version__


def repository_root(start: Path | None = None) -> Path:
    """Locate the repository root starting from *start* or CWD."""
    current = Path(start or Path.cwd()).resolve()
    for parent in [current, *current.parents]:
        if (parent / ".git").exists():
            return parent
    return current


# Backwards compatibility import for legacy entry points
from .cli import main  # noqa: E402  (import after __version__ is defined)

__all__.append("main")
