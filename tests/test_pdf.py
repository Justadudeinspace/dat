from pathlib import Path

from dat.pdf import write_pdf_report
from dat.report import build_metadata
from dat.rules import RuleFinding
from dat.scanner import FileRecord, ScanResult, ScanStatistics


def sample_result(tmp_path: Path) -> ScanResult:
    result = ScanResult(root=tmp_path)
    result.files.append(FileRecord(path="file.txt", size=20, lines=3, binary=False))
    result.stats = ScanStatistics(scanned=1, skipped=0, binary=0, errors=0)
    return result


def test_write_pdf_report(tmp_path):
    result = sample_result(tmp_path)
    metadata = build_metadata(tmp_path)
    output = tmp_path / "audit.pdf"

    write_pdf_report(output, result, [RuleFinding("id", "message", "low", "file.txt")], metadata)

    assert output.exists()
    assert output.stat().st_size > 0
