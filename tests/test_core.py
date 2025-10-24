from __future__ import annotations

import json
from pathlib import Path

from dat.integration.lrc import extract_rules_from_schema, load_integration_config, summarize_metadata
from dat.integration.signing import sign_artifact
from dat.logging.audit import append_encrypted_log, key_file, log_file


def test_lrc_helpers(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps({"schemas": [{"repos": ["demo"], "rules": [{"id": "x", "patterns": ["foo"]}]}]}), encoding="utf-8")
    config = load_integration_config(config_path)
    schema = config["schemas"][0]
    rules = extract_rules_from_schema(schema)
    assert rules[0]["id"] == "x"
    metadata = summarize_metadata({"owner": "team", "notes": "demo", "extra": "ignore"})
    assert metadata == {"owner": "team", "notes": "demo"}


def test_encrypted_log(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("DAT_CONFIG_DIR", str(tmp_path))
    append_encrypted_log({"foo": "bar"})
    assert key_file().exists()
    token = log_file().read_text(encoding="utf-8").strip()
    assert token
    # verify token decryptable
    from cryptography.fernet import Fernet

    key = key_file().read_bytes()
    data = Fernet(key).decrypt(token.encode("utf-8"))
    assert json.loads(data.decode("utf-8")) == {"foo": "bar"}


def test_sign_artifact(tmp_path: Path, monkeypatch) -> None:
    artifact = tmp_path / "artifact.json"
    artifact.write_text("{}", encoding="utf-8")
    monkeypatch.setenv("PATH", "")
    signature = sign_artifact(artifact)
    assert signature.exists()
    digest = signature.read_text(encoding="utf-8")
    assert len(digest) == 64
