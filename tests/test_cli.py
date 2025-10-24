from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture()
def sample_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "code.py").write_text("print('hello')\n# TODO: fix\n", encoding="utf-8")
    (repo / "binary.bin").write_bytes(b"\x00\x01\x02")
    return repo


def run_cli(args: list[str], env: dict[str, str] | None = None, cwd: Path | None = None) -> subprocess.CompletedProcess:
    cmd = [sys.executable, "-m", "dat.cli", *args]
    merged_env = os.environ.copy()
    merged_env.setdefault("PYTHONWARNINGS", "ignore")
    src_path = Path(__file__).resolve().parents[1] / "src"
    merged_env["PYTHONPATH"] = os.pathsep.join(
        [str(src_path)] + ([merged_env["PYTHONPATH"]] if "PYTHONPATH" in merged_env else [])
    )
    if env:
        merged_env.update(env)
    return subprocess.run(
        cmd,
        cwd=cwd,
        env=merged_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )


def test_cli_generates_signed_report(tmp_path: Path, sample_repo: Path) -> None:
    output = tmp_path / "report.jsonl"
    config_dir = tmp_path / "config"
    result = run_cli(
        ["--safe", "--report", str(output), str(sample_repo)],
        env={
            "DAT_CONFIG_DIR": str(config_dir),
            "NO_COLOR": "1",
        },
    )
    assert result.returncode == 0, result.stderr
    assert output.exists()
    data = json.loads(output.read_text(encoding="utf-8").splitlines()[0])
    assert data["repo"] == sample_repo.name
    assert "fingerprint" in data
    signature = output.with_suffix(output.suffix + ".asc")
    assert signature.exists()
    # ensure encrypted audit log exists
    log_file = config_dir / "auditlog.jsonl"
    assert log_file.exists()
    assert log_file.stat().st_size > 0


def test_cli_diff_detection(tmp_path: Path, sample_repo: Path) -> None:
    baseline = tmp_path / "baseline.json"
    config_dir = tmp_path / "config"
    baseline_result = run_cli(
        ["--report", str(baseline), str(sample_repo)],
        env={
            "DAT_CONFIG_DIR": str(config_dir),
            "NO_COLOR": "1",
        },
    )
    assert baseline_result.returncode == 0, baseline_result.stderr
    # introduce additional violation
    original = (sample_repo / "code.py").read_text(encoding="utf-8")
    (sample_repo / "code.py").write_text(original + "API_KEY=123\n", encoding="utf-8")
    result = run_cli(
        ["--report", str(tmp_path / "second.json"), "--diff", str(baseline), str(sample_repo)],
        env={
            "DAT_CONFIG_DIR": str(config_dir),
            "NO_COLOR": "1",
        },
    )
    assert result.returncode == 0
    assert "Policy regressions" in result.stdout
