from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest

from dat.scanner.core import (
    build_scan_report,
    ScanReport,
    FileReport,
    Violation
)
from dat.scanner.scanner import scan_repository, ScanResult


def write_file(path: Path, content: str) -> None:
    """Helper function to create files with proper directory structure."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_binary_file(path: Path, size: int) -> None:
    """Helper function to create binary files of specific size."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"\x00" * size)


async def _scan(root: Path, **kwargs) -> ScanReport:
    """Helper function to run scan with common parameters."""
    return await build_scan_report(
        root,
        ignore=kwargs.get("ignore", []),
        safe=kwargs.get("safe", True),
        deep=kwargs.get("deep", False),
        schema=kwargs.get("schema"),
        max_lines=kwargs.get("max_lines", 1000),
        max_size=kwargs.get("max_size", 10 * 1024 * 1024)
    )


class TestScannerCore:
    """Test core scanner functionality."""
    
    def test_scan_repository_skips_large_file(self, tmp_path: Path) -> None:
        """Test that large files are skipped in safe mode."""
        small = tmp_path / "small.txt"
        write_file(small, "hello world\n")
        
        large = tmp_path / "large.txt"
        write_file(large, "x" * (1024 * 1024 + 1))  # 1MB + 1 byte
        
        result = scan_repository(tmp_path, max_size=1024, max_lines=10)
        
        assert any(record.path == "small.txt" for record in result.files)
        assert "large.txt" in [skip.path for skip in result.skipped]
    
    def test_scan_repository_respects_ignore_patterns(self, tmp_path: Path) -> None:
        """Test file exclusion using ignore patterns."""
        write_file(tmp_path / "keep.txt", "ok\n")
        write_file(tmp_path / "ignored.log", "ignored\n")
        write_file(tmp_path / "subdir" / "also_ignored.log", "also ignored\n")
        
        result = scan_repository(tmp_path, ignore_patterns=["*.log"])
        
        # Check that log files are skipped
        assert all(record.path != "ignored.log" for record in result.files)
        assert all("also_ignored.log" not in record.path for record in result.files)
        
        # Check that non-log files are included
        assert any(record.path == "keep.txt" for record in result.files)
        
        # Verify skipped files are tracked
        skipped_paths = [skip.path for skip in result.skipped]
        assert "ignored.log" in skipped_paths
        assert "subdir/also_ignored.log" in skipped_paths
    
    def test_scan_repository_deep_mode_counts_lines(self, tmp_path: Path) -> None:
        """Test deep mode behavior with large files."""
        content = "\n".join(str(i) for i in range(0, 1500))  # 1500 lines
        write_file(tmp_path / "big.txt", content)
        
        # Safe mode should skip the file
        safe_result = scan_repository(tmp_path, max_lines=100, deep=False)
        
        # Deep mode should include the file
        deep_result = scan_repository(tmp_path, max_lines=100, deep=True, safe=False)
        
        assert "big.txt" in [skip.path for skip in safe_result.skipped]
        assert any(record.path == "big.txt" for record in deep_result.files)
    
    def test_scan_repository_binary_file_handling(self, tmp_path: Path) -> None:
        """Test handling of binary files in different modes."""
        # Create text and binary files
        write_file(tmp_path / "text.txt", "This is text content\n")
        write_binary_file(tmp_path / "binary.bin", 1024)  # 1KB binary
        
        # Safe mode (default) - should skip binary
        safe_result = scan_repository(tmp_path, safe=True)
        
        # Deep mode - should include binary
        deep_result = scan_repository(tmp_path, deep=True, safe=False)
        
        safe_files = [record.path for record in safe_result.files]
        deep_files = [record.path for record in deep_result.files]
        
        assert "text.txt" in safe_files
        assert "binary.bin" not in safe_files  # Binary skipped in safe mode
        assert "binary.bin" in deep_files  # Binary included in deep mode
    
    def test_scan_repository_complex_ignore_patterns(self, tmp_path: Path) -> None:
        """Test complex ignore pattern matching."""
        # Create various file types
        files = [
            "src/main.py",
            "src/__pycache__/module.pyc",
            "tests/test_main.py",
            "dist/app.tar.gz",
            "node_modules/package/index.js",
            "logs/app.log",
            "temp/temp_file.tmp"
        ]
        
        for file_path in files:
            write_file(tmp_path / file_path, "content")
        
        ignore_patterns = [
            "**/__pycache__/**",
            "**/*.pyc",
            "node_modules/**",
            "dist/*",
            "*.log",
            "temp/*.tmp"
        ]
        
        result = scan_repository(tmp_path, ignore_patterns=ignore_patterns)
        
        scanned_paths = [record.path for record in result.files]
        skipped_paths = [skip.path for skip in result.skipped]
        
        # Should include these files
        assert "src/main.py" in scanned_paths
        assert "tests/test_main.py" in scanned_paths
        
        # Should exclude these files
        assert "src/__pycache__/module.pyc" in skipped_paths
        assert "node_modules/package/index.js" in skipped_paths
        assert "dist/app.tar.gz" in skipped_paths
        assert "logs/app.log" in skipped_paths
        assert "temp/temp_file.tmp" in skipped_paths


class TestAsyncScanner:
    """Test async scanner functionality."""
    
    async def test_scan_respects_ignore(self, tmp_path: Path) -> None:
        """Test that ignore patterns are respected in async scanner."""
        root = tmp_path / "repo"
        root.mkdir()
        (root / "keep.txt").write_text("hello", encoding="utf-8")
        (root / "skip.log").write_text("world", encoding="utf-8")
        (root / "subdir" / "also_skip.log").write_text("nested", encoding="utf-8")
        
        report = await _scan(root, ignore=["*.log"])
        files = [entry.path for entry in report.files]
        
        # Should include text files
        assert any("keep.txt" in path for path in files)
        
        # Should exclude log files
        assert all("skip.log" not in path for path in files)
        assert all("also_skip.log" not in path for path for path in files)
    
    async def test_policy_from_schema(self, tmp_path: Path) -> None:
        """Test custom rule application from schema."""
        schema_rules = [
            {
                "id": "custom.alert",
                "patterns": ["ALERT", "CRITICAL"],
                "severity": "critical",
                "description": "Custom alert detection"
            },
            {
                "id": "custom.warning", 
                "patterns": ["WARNING"],
                "severity": "medium",
                "description": "Custom warning detection"
            }
        ]
        
        root = tmp_path / "repo"
        root.mkdir()
        (root / "file1.txt").write_text("ALERT: System failure", encoding="utf-8")
        (root / "file2.txt").write_text("WARNING: Minor issue", encoding="utf-8")
        (root / "file3.txt").write_text("Normal content", encoding="utf-8")
        
        report = await _scan(root, schema={"rules": schema_rules})
        
        # Collect all violations
        violations = []
        for file_report in report.files:
            violations.extend(file_report.violations)
        
        # Verify custom rules are applied
        assert any(v.rule_id == "custom.alert" for v in violations)
        assert any(v.rule_id == "custom.warning" for v in violations)
        
        # Verify violation details
        alert_violations = [v for v in violations if v.rule_id == "custom.alert"]
        if alert_violations:
            assert alert_violations[0].severity == "critical"
        
        warning_violations = [v for v in violations if v.rule_id == "custom.warning"]
        if warning_violations:
            assert warning_violations[0].severity == "medium"
    
    async def test_scan_safe_mode_limits(self, tmp_path: Path) -> None:
        """Test safe mode file size and line limits."""
        root = tmp_path / "repo"
        root.mkdir()
        
        # Create files of different sizes
        (root / "small.txt").write_text("Small file\n" * 10, encoding="utf-8")  # 10 lines
        (root / "large.txt").write_text("x" * (11 * 1024 * 1024), encoding="utf-8")  # 11MB
        (root / "many_lines.txt").write_text("Line\n" * 1500, encoding="utf-8")  # 1500 lines
        
        # Scan with conservative limits
        report = await _scan(
            root, 
            safe=True,
            max_size=10 * 1024 * 1024,  # 10MB
            max_lines=1000  # 1000 lines
        )
        
        scanned_files = [f.path for f in report.files]
        
        # Small file should be scanned
        assert any("small.txt" in path for path in scanned_files)
        
        # Large and many-line files should be skipped in safe mode
        large_file_scanned = any("large.txt" in path for path in scanned_files)
        many_lines_scanned = any("many_lines.txt" in path for path in scanned_files)
        
        assert not large_file_scanned, "Large file should be skipped in safe mode"
        assert not many_lines_scanned, "File with many lines should be skipped in safe mode"
    
    async def test_scan_deep_mode_no_limits(self, tmp_path: Path) -> None:
        """Test deep mode ignores size and line limits."""
        root = tmp_path / "repo"
        root.mkdir()
        
        # Create files that exceed safe mode limits
        (root / "huge.txt").write_text("x" * (50 * 1024 * 1024), encoding="utf-8")  # 50MB
        (root / "massive_lines.txt").write_text("Line\n" * 10000, encoding="utf-8")  # 10k lines
        
        # Scan in deep mode
        report = await _scan(
            root,
            safe=False,
            deep=True,
            max_size=1024,  # Very small limit
            max_lines=10    # Very small limit
        )
        
        scanned_files = [f.path for f in report.files]
        
        # Both files should be scanned despite limits in deep mode
        assert any("huge.txt" in path for path in scanned_files)
        assert any("massive_lines.txt" in path for path in scanned_files)
    
    async def test_scan_empty_repository(self, tmp_path: Path) -> None:
        """Test scanning an empty repository."""
        root = tmp_path / "empty_repo"
        root.mkdir()
        
        report = await _scan(root)
        
        assert len(report.files) == 0
        assert report.repo == root.name
        assert report.total_files == 0
        assert report.total_violations == 0
    
    async def test_scan_nested_directory_structure(self, tmp_path: Path) -> None:
        """Test scanning complex directory structures."""
        root = tmp_path / "complex_repo"
        
        # Create nested structure
        files = [
            "src/main.py",
            "src/utils/helpers.py",
            "src/utils/__init__.py",
            "tests/unit/test_main.py",
            "tests/integration/test_api.py",
            "docs/README.md",
            "docs/api/reference.md",
            "config/app.yaml",
            "config/database.yaml"
        ]
        
        for file_path in files:
            full_path = root / file_path
            write_file(full_path, f"Content for {file_path}")
        
        report = await _scan(root)
        
        # All files should be scanned
        assert len(report.files) == len(files)
        
        # Verify all files are present in report
        reported_paths = [f.path for f in report.files]
        for file_path in files:
            assert any(file_path in reported_path for reported_path in reported_paths)
    
    async def test_scan_file_types_detection(self, tmp_path: Path) -> None:
        """Test detection and handling of different file types."""
        root = tmp_path / "file_types"
        root.mkdir()
        
        # Create various file types
        file_contents = {
            "script.py": "import os\nprint('Hello')\n# TODO: fix",
            "document.md": "# Header\nSome **markdown** content",
            "config.json": '{"key": "value", "secret": "password123"}',
            "data.csv": "name,age\nJohn,30\nJane,25",
            "binary.data": b"\x00\x01\x02\x03\x04\x05"
        }
        
        for filename, content in file_contents.items():
            file_path = root / filename
            if isinstance(content, bytes):
                file_path.write_bytes(content)
            else:
                file_path.write_text(content, encoding="utf-8")
        
        report = await _scan(root, deep=True)
        
        # All files should be scanned in deep mode
        assert len(report.files) == len(file_contents)
        
        # Verify file type detection in report
        for file_report in report.files:
            assert file_report.size > 0
            assert file_report.path in file_contents.keys()


class TestScannerEdgeCases:
    """Test scanner edge cases and error conditions."""
    
    async def test_scan_nonexistent_directory(self) -> None:
        """Test scanning non-existent directory."""
        nonexistent_path = Path("/nonexistent/path/that/does/not/exist")
        
        with pytest.raises(FileNotFoundError):
            await _scan(nonexistent_path)
    
    async def test_scan_permission_denied(self, tmp_path: Path) -> None:
        """Test handling of permission denied errors."""
        if hasattr(os, 'chmod'):
            root = tmp_path / "restricted"
            root.mkdir()
            restricted_file = root / "restricted.txt"
            restricted_file.write_text("content", encoding="utf-8")
            
            # Make file unreadable
            os.chmod(restricted_file, 0o000)
            
            try:
                report = await _scan(root)
                # Should complete scan but track the error
                assert len(report.files) == 0
                # Error should be recorded (implementation specific)
            finally:
                # Restore permissions for cleanup
                os.chmod(restricted_file, 0o644)
    
    async def test_scan_symlink_handling(self, tmp_path: Path) -> None:
        """Test handling of symbolic links."""
        if hasattr(os, 'symlink'):  # Skip on Windows without symlink support
            root = tmp_path / "with_links"
            root.mkdir()
            
            # Create target file
            target = root / "target.txt"
            target.write_text("target content", encoding="utf-8")
            
            # Create symlink
            link = root / "link.txt"
            os.symlink(target, link)
            
            report = await _scan(root)
            
            # Should follow symlinks and scan the content
            scanned_paths = [f.path for f in report.files]
            assert "target.txt" in scanned_paths
            # Symlink itself might or might not be included based on implementation
    
    async def test_scan_very_large_repository(self, tmp_path: Path) -> None:
        """Test performance with many files."""
        root = tmp_path / "large_repo"
        root.mkdir()
        
        # Create many small files
        for i in range(100):
            file_path = root / f"file_{i:03d}.txt"
            file_path.write_text(f"Content of file {i}", encoding="utf-8")
        
        report = await _scan(root)
        
        # Should scan all files
        assert len(report.files) == 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
