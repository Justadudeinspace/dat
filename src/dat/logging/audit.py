"""Encrypted audit logging."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict

from cryptography.fernet import Fernet

def config_dir() -> Path:
    return Path(os.environ.get("DAT_CONFIG_DIR", Path.home() / ".config" / "dat"))


def log_file() -> Path:
    return config_dir() / "auditlog.jsonl"


def key_file() -> Path:
    return config_dir() / "auditlog.key"


def _ensure_key() -> bytes:
    key_path = key_file()
    cfg_dir = key_path.parent
    cfg_dir.mkdir(parents=True, exist_ok=True)
    if key_path.exists():
        return key_path.read_bytes()
    key = Fernet.generate_key()
    key_path.write_bytes(key)
    os.chmod(key_path, 0o600)
    return key


def append_encrypted_log(payload: Dict[str, Any]) -> None:
    """Encrypt and persist *payload* into :data:`LOG_FILE`."""

    key = _ensure_key()
    token = Fernet(key).encrypt(json.dumps(payload, sort_keys=True).encode("utf-8"))
    log_path = log_file()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("ab") as handle:
        handle.write(token + b"\n")
