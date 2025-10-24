import json
from pathlib import Path

import pytest

from dat import __version__, cli


def test_version_flag_prints_version(capsys):
    with pytest.raises(SystemExit) as exc:
        cli.parse_args(["--version"])
    assert exc.value.code == 0
    assert capsys.readouterr().out.strip() == __version__


def test_cli_generates_json_report(tmp_path, capsys):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "file.txt").write_text("content", encoding="utf-8")
    report_path = tmp_path / "report.json"

    exit_code = cli.main([str(repo), "--report", str(report_path)])

    assert exit_code == 0
    assert report_path.exists()
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["metadata"]["dat_version"] == __version__


def test_cli_from_lrc_writes_audit(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "file.txt").write_text("content", encoding="utf-8")
    (repo / ".lrc-build.json").write_text(json.dumps({"project": "demo"}), encoding="utf-8")

    exit_code = cli.main([str(repo), "--from-lrc"])

    assert exit_code == 0
    audit_path = repo / ".lrc-audit.json"
    assert audit_path.exists()
