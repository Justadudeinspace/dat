from pathlib import Path

from dat.report import build_metadata, write_json_report, write_markdown_report
from dat.rules import RuleFinding
from dat.scanner import FileRecord, ScanResult, ScanStatistics


def sample_result(tmp_path: Path) -> ScanResult:
    result = ScanResult(root=tmp_path)
    result.files.append(FileRecord(path="a.txt", size=10, lines=2, binary=False))
    result.stats = ScanStatistics(scanned=1, skipped=0, binary=0, errors=0)
    return result


def test_write_json_report(tmp_path):
    result = sample_result(tmp_path)
    metadata = build_metadata(tmp_path)
    output = tmp_path / "audit.json"

    write_json_report(output, result, [RuleFinding("id", "message", "low", "a.txt")], metadata)

    data = output.read_text(encoding="utf-8")
    assert "\n" == data[-1]
    assert "audit.json" in str(output)


def test_write_markdown_report(tmp_path):
    result = sample_result(tmp_path)
    metadata = build_metadata(tmp_path)
    output = tmp_path / "audit.md"

    write_markdown_report(output, result, [], metadata)

    text = output.read_text(encoding="utf-8")
    assert text.startswith("# DAT Audit Report")
