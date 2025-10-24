from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from cryptography.fernet import Fernet

from dat.integration.lrc import (
    extract_rules_from_schema, 
    load_integration_config, 
    summarize_metadata,
    select_schema,
    merge_lrc_metadata
)
from dat.integration.signing import sign_artifact, verify_signature
from dat.logging.audit import (
    append_encrypted_log, 
    key_file, 
    log_file,
    read_audit_log,
    rotate_audit_key
)


class TestLRCIntegration:
    """Test LRC (License and Regulatory Compliance) integration features."""
    
    def test_load_integration_config_valid_file(self, tmp_path: Path) -> None:
        """Test loading valid LRC configuration file."""
        config_path = tmp_path / "lrc_config.json"
        config_data = {
            "schemas": [
                {
                    "repos": ["demo", "test-.*"],
                    "owner": "security-team",
                    "compliance": ["soc2", "gdpr"],
                    "rules": [
                        {
                            "id": "lrc.no-secrets",
                            "patterns": ["SECRET=", "API_KEY\\s*="],
                            "severity": "critical",
                            "description": "Hardcoded secrets detection"
                        }
                    ]
                }
            ],
            "policy": {
                "require_signing": True,
                "max_critical_violations": 0
            }
        }
        config_path.write_text(json.dumps(config_data), encoding="utf-8")
        
        config = load_integration_config(config_path)
        
        assert config is not None
        assert "schemas" in config
        assert len(config["schemas"]) == 1
        assert config["schemas"][0]["owner"] == "security-team"
        assert "policy" in config
        assert config["policy"]["require_signing"] is True

    def test_load_integration_config_invalid_json(self, tmp_path: Path) -> None:
        """Test handling of invalid JSON configuration."""
        config_path = tmp_path / "invalid_config.json"
        config_path.write_text("{ invalid json }", encoding="utf-8")
        
        config = load_integration_config(config_path)
        
        # Should return empty default config
        assert config == {"schemas": []}

    def test_load_integration_config_nonexistent_file(self) -> None:
        """Test handling of non-existent configuration file."""
        config = load_integration_config(Path("/nonexistent/path/config.json"))
        
        assert config == {"schemas": []}

    def test_load_integration_config_auto_detection(self, tmp_path: Path, monkeypatch) -> None:
        """Test automatic configuration file detection."""
        config_dir = tmp_path / ".config" / "lrc"
        config_dir.mkdir(parents=True)
        config_path = config_dir / "dat_integration.json"
        
        config_data = {
            "schemas": [{"repos": ["auto-detected"], "rules": []}]
        }
        config_path.write_text(json.dumps(config_data), encoding="utf-8")
        
        # Test with environment variable
        monkeypatch.setenv("LRC_CONFIG_PATH", str(config_path))
        config = load_integration_config()
        
        assert config["schemas"][0]["repos"] == ["auto-detected"]

    def test_extract_rules_from_schema_comprehensive(self) -> None:
        """Test comprehensive rule extraction from schema."""
        schema = {
            "repos": ["test-repo"],
            "rules": [
                {
                    "id": "lrc.security.secret",
                    "patterns": ["password\\s*=", "secret_key\\s*="],
                    "severity": "critical",
                    "description": "Hardcoded credentials",
                    "category": "security"
                },
                {
                    "id": "lrc.compliance.license",
                    "patterns": ["GPL-", "AGPL-"],
                    "severity": "high",
                    "description": "Restricted license header"
                }
            ]
        }
        
        rules = extract_rules_from_schema(schema)
        
        assert len(rules) == 2
        assert rules[0]["id"] == "lrc.security.secret"
        assert rules[0]["severity"] == "critical"
        assert rules[0]["category"] == "security"
        assert rules[1]["id"] == "lrc.compliance.license"
        assert rules[1]["severity"] == "high"

    def test_extract_rules_from_schema_default_severity(self) -> None:
        """Test rule extraction with default severity."""
        schema = {
            "repos": ["test-repo"],
            "rules": [
                {
                    "id": "lrc.test.rule",
                    "patterns": ["test_pattern"]
                    # No severity specified, should default to "medium"
                }
            ]
        }
        
        rules = extract_rules_from_schema(schema)
        
        assert rules[0]["id"] == "lrc.test.rule"
        assert rules[0]["severity"] == "medium"  # Default value

    def test_summarize_metadata_comprehensive(self) -> None:
        """Test metadata summarization with various field types."""
        full_metadata = {
            "owner": "security-team",
            "compliance": ["soc2", "gdpr"],
            "notes": "Production deployment",
            "repository": "https://github.com/org/repo",
            "version": "1.2.3",
            "build_id": "build-12345",
            "extra_field": "should_be_ignored",
            "internal_data": "confidential"
        }
        
        summarized = summarize_metadata(full_metadata)
        
        # Should include standard fields
        assert "owner" in summarized
        assert "compliance" in summarized
        assert "notes" in summarized
        assert "repository" in summarized
        assert "version" in summarized
        assert "build_id" in summarized
        
        # Should exclude non-standard fields
        assert "extra_field" not in summarized
        assert "internal_data" not in summarized
        
        # Values should be preserved
        assert summarized["owner"] == "security-team"
        assert summarized["compliance"] == ["soc2", "gdpr"]

    def test_select_schema_repo_matching(self) -> None:
        """Test schema selection based on repository name patterns."""
        config = {
            "schemas": [
                {
                    "repos": ["dat", "enterprise-.*"],
                    "owner": "platform-team",
                    "rules": []
                },
                {
                    "repos": ["web-.*", "api-.*"],
                    "owner": "web-team", 
                    "rules": []
                },
                {
                    "repos": [],  # Default schema for all repos
                    "owner": "default-team",
                    "rules": []
                }
            ]
        }
        
        # Test exact match
        schema1 = select_schema(config, "dat")
        assert schema1["owner"] == "platform-team"
        
        # Test regex match
        schema2 = select_schema(config, "enterprise-core")
        assert schema2["owner"] == "platform-team"
        
        # Test different pattern
        schema3 = select_schema(config, "web-frontend")
        assert schema3["owner"] == "web-team"
        
        # Test default schema
        schema4 = select_schema(config, "unknown-repo")
        assert schema4["owner"] == "default-team"

    def test_merge_lrc_metadata(self) -> None:
        """Test merging of LRC metadata from multiple sources."""
        config_metadata = {
            "owner": "config-owner",
            "compliance": ["soc2"],
            "policy": {"strict": True}
        }
        
        build_metadata = {
            "build_id": "build-123",
            "commit_hash": "abc123",
            "version": "1.0.0",
            "owner": "build-owner"  # Should override config
        }
        
        merged = merge_lrc_metadata(config_metadata, build_metadata)
        
        # Build metadata should override config
        assert merged["owner"] == "build-owner"
        # Other config fields should be preserved
        assert merged["compliance"] == ["soc2"]
        # Build fields should be included
        assert merged["build_id"] == "build-123"
        assert merged["commit_hash"] == "abc123"
        # Policy should be preserved
        assert merged["policy"] == {"strict": True}


class TestSigningIntegration:
    """Test artifact signing and verification functionality."""
    
    def test_sign_artifact_success(self, tmp_path: Path) -> None:
        """Test successful artifact signing."""
        artifact = tmp_path / "test_artifact.json"
        artifact.write_text('{"data": "test content"}', encoding="utf-8")
        
        signature_path = sign_artifact(artifact)
        
        assert signature_path.exists()
        assert signature_path.name == "test_artifact.json.asc"
        
        # Verify signature content
        signature_content = signature_path.read_text(encoding="utf-8")
        assert signature_content.strip()  # Should not be empty
        
    def test_sign_artifact_nonexistent(self, tmp_path: Path) -> None:
        """Test signing non-existent artifact."""
        artifact = tmp_path / "nonexistent.json"
        
        with pytest.raises(FileNotFoundError):
            sign_artifact(artifact)
    
    def test_verify_signature_success(self, tmp_path: Path) -> None:
        """Test signature verification for valid artifacts."""
        artifact = tmp_path / "valid_artifact.json"
        original_content = '{"valid": "data"}'
        artifact.write_text(original_content, encoding="utf-8")
        
        # Create signature
        signature_path = sign_artifact(artifact)
        
        # Verify signature
        is_valid = verify_signature(artifact, signature_path)
        
        assert is_valid is True
    
    def test_verify_signature_tampered(self, tmp_path: Path) -> None:
        """Test signature verification for tampered artifacts."""
        artifact = tmp_path / "tampered_artifact.json"
        original_content = '{"valid": "data"}'
        artifact.write_text(original_content, encoding="utf-8")
        
        # Create signature
        signature_path = sign_artifact(artifact)
        
        # Tamper with the artifact
        artifact.write_text('{"tampered": "data"}', encoding="utf-8")
        
        # Verification should fail
        is_valid = verify_signature(artifact, signature_path)
        
        assert is_valid is False
    
    def test_verify_signature_missing_files(self, tmp_path: Path) -> None:
        """Test signature verification with missing files."""
        artifact = tmp_path / "artifact.json"
        signature = tmp_path / "signature.asc"
        
        # Both files missing
        assert verify_signature(artifact, signature) is False
        
        # Only artifact exists
        artifact.write_text("content", encoding="utf-8")
        assert verify_signature(artifact, signature) is False
        
        # Only signature exists  
        signature.write_text("sig", encoding="utf-8")
        artifact.unlink()
        assert verify_signature(artifact, signature) is False


class TestAuditLogging:
    """Test encrypted audit logging functionality."""
    
    def test_encrypted_log_creation(self, tmp_path: Path, monkeypatch) -> None:
        """Test creation of encrypted audit log entries."""
        monkeypatch.setenv("DAT_CONFIG_DIR", str(tmp_path))
        
        log_data = {
            "timestamp": "2024-01-15T10:30:00Z",
            "user": "testuser",
            "action": "scan",
            "repo": "test-repo",
            "violations": 5
        }
        
        append_encrypted_log(log_data)
        
        # Verify key and log files created
        assert key_file().exists()
        assert log_file().exists()
        
        # Verify log file has content
        log_content = log_file().read_text(encoding="utf-8").strip()
        assert log_content
        
        # Verify encryption by decrypting
        key = key_file().read_bytes()
        fernet = Fernet(key)
        decrypted_data = fernet.decrypt(log_content.encode("utf-8"))
        parsed_data = json.loads(decrypted_data.decode("utf-8"))
        
        assert parsed_data == log_data
    
    def test_encrypted_log_multiple_entries(self, tmp_path: Path, monkeypatch) -> None:
        """Test multiple log entries are properly appended."""
        monkeypatch.setenv("DAT_CONFIG_DIR", str(tmp_path))
        
        entries = [
            {"entry": 1, "action": "start"},
            {"entry": 2, "action": "scan"},
            {"entry": 3, "action": "complete"}
        ]
        
        for entry in entries:
            append_encrypted_log(entry)
        
        # Read all log entries
        all_entries = read_audit_log()
        
        assert len(all_entries) == 3
        for i, entry in enumerate(all_entries):
            assert entry["entry"] == i + 1
    
    def test_read_audit_log_empty(self, tmp_path: Path, monkeypatch) -> None:
        """Test reading from non-existent or empty audit log."""
        monkeypatch.setenv("DAT_CONFIG_DIR", str(tmp_path))
        
        entries = read_audit_log()
        
        assert entries == []
    
    def test_audit_log_key_rotation(self, tmp_path: Path, monkeypatch) -> None:
        """Test audit log key rotation functionality."""
        monkeypatch.setenv("DAT_CONFIG_DIR", str(tmp_path))
        
        # Create initial log entry
        append_encrypted_log({"test": "initial"})
        original_key = key_file().read_bytes()
        
        # Rotate key
        rotate_audit_key()
        new_key = key_file().read_bytes()
        
        # Keys should be different
        assert original_key != new_key
        
        # Old log entries should still be readable
        entries = read_audit_log()
        assert len(entries) == 1
        assert entries[0]["test"] == "initial"
        
        # New entries should use new key
        append_encrypted_log({"test": "after_rotation"})
        entries = read_audit_log()
        assert len(entries) == 2
    
    def test_encrypted_log_large_data(self, tmp_path: Path, monkeypatch) -> None:
        """Test logging of large data payloads."""
        monkeypatch.setenv("DAT_CONFIG_DIR", str(tmp_path))
        
        large_data = {
            "timestamp": "2024-01-15T10:30:00Z",
            "user": "testuser",
            "large_field": "x" * 10000,  # 10KB of data
            "nested": {
                "level1": {"level2": {"level3": "deeply_nested"}},
                "array": list(range(1000))
            }
        }
        
        append_encrypted_log(large_data)
        
        # Verify the entry can be read back
        entries = read_audit_log()
        assert len(entries) == 1
        assert entries[0]["large_field"] == "x" * 10000
        assert entries[0]["nested"]["level1"]["level2"]["level3"] == "deeply_nested"
    
    def test_encrypted_log_invalid_data(self, tmp_path: Path, monkeypatch) -> None:
        """Test handling of invalid log data."""
        monkeypatch.setenv("DAT_CONFIG_DIR", str(tmp_path))
        
        # Non-serializable data should raise an error
        class NonSerializable:
            pass
        
        with pytest.raises(Exception):
            append_encrypted_log({"invalid": NonSerializable()})


def test_integration_workflow(tmp_path: Path, monkeypatch) -> None:
    """Test complete LRC integration workflow."""
    # Set up test environment
    monkeypatch.setenv("DAT_CONFIG_DIR", str(tmp_path))
    
    # Create LRC configuration
    config_dir = tmp_path / ".config" / "lrc"
    config_dir.mkdir(parents=True)
    config_path = config_dir / "dat_integration.json"
    
    config_data = {
        "schemas": [
            {
                "repos": ["test-repo"],
                "owner": "test-team",
                "compliance": ["soc2"],
                "rules": [
                    {
                        "id": "test.rule.1",
                        "patterns": ["TEST_PATTERN"],
                        "severity": "medium"
                    }
                ]
            }
        ]
    }
    config_path.write_text(json.dumps(config_data), encoding="utf-8")
    
    # Load configuration
    config = load_integration_config(config_path)
    assert config["schemas"][0]["owner"] == "test-team"
    
    # Extract rules
    schema = config["schemas"][0]
    rules = extract_rules_from_schema(schema)
    assert len(rules) == 1
    assert rules[0]["id"] == "test.rule.1"
    
    # Create and sign an artifact
    artifact = tmp_path / "scan_report.json"
    artifact.write_text('{"scan": "results"}', encoding="utf-8")
    signature = sign_artifact(artifact)
    assert signature.exists()
    
    # Log the activity
    log_data = {
        "timestamp": "2024-01-15T10:30:00Z",
        "action": "integration_test",
        "artifact": str(artifact)
    }
    append_encrypted_log(log_data)
    
    # Verify log was written
    entries = read_audit_log()
    assert len(entries) == 1
    assert entries[0]["action"] == "integration_test"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
