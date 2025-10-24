from pathlib import Path

from dat import integration
from dat.rules import RuleFinding
from dat.scanner import FileRecord, ScanResult, ScanStatistics


def sample_result(tmp_path: Path) -> ScanResult:
    result = ScanResult(root=tmp_path)
    result.files.append(FileRecord(path="file.txt", size=1, lines=1, binary=False))
    result.stats = ScanStatistics(scanned=1, skipped=0, binary=0, errors=0)
    return result


def test_merge_lrc_metadata():
    config = {"project": "alpha", "settings": {"sign": True}}
    build = {"settings": {"sign": False}, "version": "1"}

    merged = integration.merge_lrc_metadata(config, build)

    assert merged["project"] == "alpha"
    assert merged["settings"]["sign"] is False
    assert merged["version"] == "1"


def test_write_lrc_audit(tmp_path):
    result = sample_result(tmp_path)
    metadata = {"dat_version": "3", "generated_at": "now"}
    output = integration.write_lrc_audit(tmp_path, result, [RuleFinding("id", "msg", "low", None)], metadata)

    assert output.exists()
    data = output.read_text(encoding="utf-8")
    assert data.endswith("\n")
