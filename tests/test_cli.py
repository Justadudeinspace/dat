from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from dat import __version__, cli


@pytest.fixture()
def sample_repo(tmp_path: Path) -> Path:
    """Create a sample repository with various file types for testing."""
    repo = tmp_path / "test_repo"
    repo.mkdir()
    
    # Create source code files
    (repo / "main.py").write_text("print('hello world')\n# TODO: fix this later\n", encoding="utf-8")
    (repo / "config.py").write_text("DATABASE_URL = 'postgresql://localhost:5432'\nAPI_KEY = 'test123'\n", encoding="utf-8")
    (repo / "utils.py").write_text("import os\nimport sys\n\ndef helper():\n    pass\n", encoding="utf-8")
    
    # Create documentation
    (repo / "README.md").write_text("# Test Repository\n\nThis is a test repo for DAT scanning.\n", encoding="utf-8")
    
    # Create binary file
    (repo / "binary.bin").write_bytes(b"\x00\x01\x02\x03\x04\x05")
    
    # Create hidden file
    (repo / ".env").write_text("SECRET_KEY=abc123\nDEBUG=True\n", encoding="utf-8")
    
    # Create subdirectory structure
    (repo / "src").mkdir()
    (repo / "src" / "__init__.py").write_text("", encoding="utf-8")
    (repo / "src" / "module.py").write_text("class TestClass:\n    pass\n", encoding="utf-8")
    
    return repo


@pytest.fixture()
def lrc_config_repo(tmp_path: Path) -> Path:
    """Create a repository with LRC configuration for integration testing."""
    repo = tmp_path / "lrc_repo"
    repo.mkdir()
    
    # Create sample code
    (repo / "app.py").write_text("import os\n\nDEBUG = True\n", encoding="utf-8")
    
    # Create LRC build metadata
    lrc_build = {
        "build_id": "test-build-123",
        "commit_hash": "a1b2c3d4e5f6",
        "branch": "main",
        "version": "1.0.0",
        "artifacts": ["app.py", "requirements.txt"]
    }
    (repo / ".lrc-build.json").write_text(json.dumps(lrc_build), encoding="utf-8")
    
    return repo


def run_cli(args: list[str], env: dict[str, str] | None = None, cwd: Path | None = None) -> subprocess.CompletedProcess:
    """
    Run DAT CLI as a subprocess for integration testing.
    
    Args:
        args: Command line arguments
        env: Environment variables
        cwd: Working directory
        
    Returns:
        CompletedProcess with returncode, stdout, stderr
    """
    cmd = [sys.executable, "-m", "dat.cli", *args]
    merged_env = os.environ.copy()
    
    # Set up Python path and warnings
    merged_env.setdefault("PYTHONWARNINGS", "ignore")
    src_path = Path(__file__).resolve().parents[1] / "src"
    python_paths = [str(src_path)]
    if "PYTHONPATH" in merged_env:
        python_paths.append(merged_env["PYTHONPATH"])
    merged_env["PYTHONPATH"] = os.pathsep.join(python_paths)
    
    # Disable colors for consistent test output
    merged_env["NO_COLOR"] = "1"
    merged_env["DAT_NO_COLOR"] = "1"
    
    # Update with test-specific environment
    if env:
        merged_env.update(env)
    
    return subprocess.run(
        cmd,
        cwd=cwd,
        env=merged_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=30,  # Prevent hanging tests
        check=False,
    )


def test_version_flag_prints_version(capsys: pytest.CaptureFixture) -> None:
    """Test that --version flag prints version and exits successfully."""
    with pytest.raises(SystemExit) as exc:
        cli.parse_args(["--version"])
    assert exc.value.code == 0
    captured = capsys.readouterr()
    assert captured.out.strip() == __version__
    assert captured.err == ""


def test_cli_generates_json_report(tmp_path: Path, sample_repo: Path) -> None:
    """Test basic JSON report generation."""
    report_path = tmp_path / "report.json"
    
    exit_code = cli.main([str(sample_repo), "--report", str(report_path)])
    
    assert exit_code == 0
    assert report_path.exists()
    
    # Validate report structure
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["metadata"]["dat_version"] == __version__
    assert "scan" in payload
    assert "findings" in payload
    assert "files" in payload["scan"]


def test_cli_from_lrc_writes_audit(tmp_path: Path, lrc_config_repo: Path) -> None:
    """Test LRC integration writes audit file."""
    exit_code = cli.main([str(lrc_config_repo), "--from-lrc"])
    
    assert exit_code == 0
    audit_path = lrc_config_repo / ".lrc-audit.json"
    assert audit_path.exists()
    
    # Validate audit file content
    audit_data = json.loads(audit_path.read_text(encoding="utf-8"))
    assert "metadata" in audit_data
    assert "summary" in audit_data
    assert "findings" in audit_data
    assert "build_context" in audit_data


def test_cli_generates_signed_report(tmp_path: Path, sample_repo: Path) -> None:
    """Test report generation with signing and audit logging."""
    output = tmp_path / "report.jsonl"
    config_dir = tmp_path / "config"
    
    result = run_cli(
        ["--safe", "--report", str(output), str(sample_repo)],
        env={
            "DAT_CONFIG_DIR": str(config_dir),
        },
    )
    
    assert result.returncode == 0, f"CLI failed: {result.stderr}"
    assert output.exists()
    
    # Validate report content
    data = json.loads(output.read_text(encoding="utf-8").splitlines()[0])
    assert data["repo"] == sample_repo.name
    assert "fingerprint" in data
    assert "timestamp" in data
    assert "user" in data
    assert "report" in data
    
    # Check signature file
    signature = output.with_suffix(output.suffix + ".asc")
    assert signature.exists()
    assert signature.stat().st_size > 0
    
    # Verify encrypted audit log
    log_file = config_dir / "auditlog.jsonl"
    assert log_file.exists()
    assert log_file.stat().st_size > 0


def test_cli_diff_detection(tmp_path: Path, sample_repo: Path) -> None:
    """Test diff functionality for detecting changes between scans."""
    baseline = tmp_path / "baseline.json"
    config_dir = tmp_path / "config"
    
    # Create baseline scan
    baseline_result = run_cli(
        ["--report", str(baseline), str(sample_repo)],
        env={
            "DAT_CONFIG_DIR": str(config_dir),
        },
    )
    assert baseline_result.returncode == 0, f"Baseline scan failed: {baseline_result.stderr}"
    
    # Introduce additional violation
    original_content = (sample_repo / "config.py").read_text(encoding="utf-8")
    (sample_repo / "config.py").write_text(
        original_content + "\n# New violation\nSECRET_KEY = 'very-secret-key-123'\n", 
        encoding="utf-8"
    )
    
    # Run comparison scan
    second_report = tmp_path / "second.json"
    result = run_cli(
        ["--report", str(second_report), "--diff", str(baseline), str(sample_repo)],
        env={
            "DAT_CONFIG_DIR": str(config_dir),
        },
    )
    
    assert result.returncode == 0
    assert "Policy regressions" in result.stdout or "Differences detected" in result.stdout


def test_cli_safe_mode_respects_limits(tmp_path: Path, sample_repo: Path) -> None:
    """Test that safe mode respects file size and line limits."""
    # Create a large file that should be skipped in safe mode
    large_file = sample_repo / "large_file.txt"
    large_content = "line\n" * 2000  # 2000 lines > default 1000 limit
    large_file.write_text(large_content, encoding="utf-8")
    
    report_path = tmp_path / "safe_report.json"
    exit_code = cli.main([str(sample_repo), "--safe", "--report", str(report_path)])
    
    assert exit_code == 0
    assert report_path.exists()
    
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    scanned_files = payload["scan"]["files"]
    
    # The large file should be skipped in safe mode
    large_file_scanned = any(f["path"] == str(large_file.relative_to(sample_repo)) for f in scanned_files)
    assert not large_file_scanned, "Large file should be skipped in safe mode"


def test_cli_deep_mode_includes_all_files(tmp_path: Path, sample_repo: Path) -> None:
    """Test that deep mode includes files that would be skipped in safe mode."""
    # Create files that would normally be skipped
    large_file = sample_repo / "large.txt"
    large_file.write_text("x" * (11 * 1024 * 1024), encoding="utf-8")  # 11MB > 10MB default
    
    binary_file = sample_repo / "binary.data"
    binary_file.write_bytes(b"\x00" * 1024)
    
    report_path = tmp_path / "deep_report.json"
    exit_code = cli.main([str(sample_repo), "--deep", "--report", str(report_path)])
    
    assert exit_code == 0
    assert report_path.exists()
    
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    scanned_files = [f["path"] for f in payload["scan"]["files"]]
    
    # Both files should be included in deep mode
    assert str(large_file.relative_to(sample_repo)) in scanned_files
    assert str(binary_file.relative_to(sample_repo)) in scanned_files


def test_cli_ignore_patterns(tmp_path: Path, sample_repo: Path) -> None:
    """Test file exclusion with ignore patterns."""
    report_path = tmp_path / "ignore_report.json"
    
    exit_code = cli.main([
        str(sample_repo), 
        "--report", str(report_path),
        "--ignore", "*.py",
        "--ignore", "*.bin"
    ])
    
    assert exit_code == 0
    assert report_path.exists()
    
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    scanned_files = [f["path"] for f in payload["scan"]["files"]]
    
    # Python and binary files should be excluded
    py_files = [f for f in scanned_files if f.endswith('.py')]
    bin_files = [f for f in scanned_files if f.endswith('.bin')]
    
    assert len(py_files) == 0, "Python files should be ignored"
    assert len(bin_files) == 0, "Binary files should be ignored"


def test_cli_interactive_mode(tmp_path: Path, sample_repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test interactive mode with user confirmation."""
    # Simulate user input 'y' for confirmation
    monkeypatch.setattr('builtins.input', lambda _: 'y')
    
    report_path = tmp_path / "interactive_report.json"
    exit_code = cli.main([
        str(sample_repo),
        "--interactive",
        "--report", str(report_path)
    ])
    
    assert exit_code == 0
    assert report_path.exists()


def test_cli_verbose_output(tmp_path: Path, sample_repo: Path, capsys: pytest.CaptureFixture) -> None:
    """Test verbose mode provides detailed output."""
    report_path = tmp_path / "verbose_report.json"
    
    exit_code = cli.main([
        str(sample_repo),
        "--verbose",
        "--report", str(report_path)
    ])
    
    assert exit_code == 0
    captured = capsys.readouterr()
    
    # Verbose mode should output scan statistics
    assert "scanned" in captured.out.lower() or "files" in captured.out.lower()


def test_cli_invalid_path_handling() -> None:
    """Test graceful handling of invalid repository paths."""
    invalid_path = "/nonexistent/path/that/does/not/exist"
    
    exit_code = cli.main([invalid_path])
    
    assert exit_code != 0  # Should return error code for invalid path


def test_cli_pdf_report_generation(tmp_path: Path, sample_repo: Path) -> None:
    """Test PDF report generation."""
    pdf_path = tmp_path / "report.pdf"
    
    exit_code = cli.main([
        str(sample_repo),
        "--pdf", str(pdf_path)
    ])
    
    assert exit_code == 0
    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 0


def test_cli_multiple_output_formats(tmp_path: Path, sample_repo: Path) -> None:
    """Test generating multiple report formats simultaneously."""
    json_path = tmp_path / "report.json"
    pdf_path = tmp_path / "report.pdf"
    jsonl_path = tmp_path / "report.jsonl"
    
    exit_code = cli.main([
        str(sample_repo),
        "--report", str(json_path),
        "--pdf", str(pdf_path),
        "--jsonl", str(jsonl_path)
    ])
    
    assert exit_code == 0
    assert json_path.exists()
    assert pdf_path.exists()
    assert jsonl_path.exists()


def test_cli_no_sign_option(tmp_path: Path, sample_repo: Path) -> None:
    """Test that --no-sign disables artifact signing."""
    report_path = tmp_path / "unsigned_report.json"
    config_dir = tmp_path / "config"
    
    result = run_cli(
        ["--report", str(report_path), "--no-sign", str(sample_repo)],
        env={
            "DAT_CONFIG_DIR": str(config_dir),
        },
    )
    
    assert result.returncode == 0
    assert report_path.exists()
    
    # Signature file should not exist when --no-sign is used
    signature = report_path.with_suffix(report_path.suffix + ".asc")
    assert not signature.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
