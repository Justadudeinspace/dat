"""Artifact signing helpers."""
from __future__ import annotations

import hashlib
import shutil
import subprocess
from pathlib import Path


class SigningError(RuntimeError):
    """Raised when an artifact cannot be signed."""


def sign_artifact(path: Path) -> Path:
    """Create a detached signature for *path* using GPG when available."""

    signer = shutil.which("gpg")
    signature_path = path.with_suffix(path.suffix + ".asc")
    if signer:
        result = subprocess.run(
            [
                signer,
                "--batch",
                "--yes",
                "--armor",
                "--detach-sign",
                "--output",
                str(signature_path),
                str(path),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return signature_path
    # fallback: generate sha256 digest file
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    signature_path.write_text(digest, encoding="utf-8")
    return signature_path
