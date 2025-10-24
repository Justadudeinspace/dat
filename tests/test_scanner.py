from pathlib import Path

from dat import scanner


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_scan_repository_skips_large_file(tmp_path):
    small = tmp_path / "small.txt"
    write_file(small, "hello world\n")
    large = tmp_path / "large.txt"
    write_file(large, "x" * (1024 * 1024 + 1))

    result = scanner.scan_repository(tmp_path, max_size=1024, max_lines=10)

    assert any(record.path == "small.txt" for record in result.files)
    assert "large.txt" in result.skipped


def test_scan_repository_respects_ignore_patterns(tmp_path):
    write_file(tmp_path / "keep.txt", "ok\n")
    write_file(tmp_path / "ignored.log", "ignored\n")

    result = scanner.scan_repository(tmp_path, ignore_patterns=["*.log"])

    assert all(record.path != "ignored.log" for record in result.files)
    assert "ignored.log" in result.skipped


def test_scan_repository_deep_mode_counts_lines(tmp_path):
    content = "\n".join(str(i) for i in range(0, 1500))
    write_file(tmp_path / "big.txt", content)

    safe_result = scanner.scan_repository(tmp_path, max_lines=100, deep=False)
    deep_result = scanner.scan_repository(tmp_path, max_lines=100, deep=True, safe=False)

    assert "big.txt" in safe_result.skipped
    assert any(record.path == "big.txt" for record in deep_result.files)
