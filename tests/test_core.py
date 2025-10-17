#!/usr/bin/env python3
import os
import tempfile
import shutil
import pytest
from pathlib import Path
import sys
import io

# Add the parent directory to sys.path to import the main module
sys.path.insert(0, str(Path(__file__).parent.parent))

from dat import (
    cat_file,
    cat_all,
    print_summary,
    should_process_file,
    get_file_color,
    format_size,
    is_text_file,
    get_file_mime_type,
    DOC_EXTENSIONS,
    CODE_EXTENSIONS,
    MEDIA_EXTENSIONS,
    STATS,
    TOP_LINES,
    TOP_SIZE
)


@pytest.fixture(scope="function")
def tmp_test_dir():
    """Create a temporary directory with nested files for testing."""
    tmp_dir = tempfile.mkdtemp(prefix="dat_test_")
    
    # Create directory structure
    os.makedirs(os.path.join(tmp_dir, "subdir"), exist_ok=True)
    os.makedirs(os.path.join(tmp_dir, ".hidden_dir"), exist_ok=True)

    # Create example files
    files = {
        "root.txt": "This is the root file.\nWith multiple lines.\n",
        "config.py": "# Configuration file\nkey = 'value'\nflag = True\n",
        "script.js": "// JavaScript file\nconsole.log('Hello World');\n",
        "document.md": "# Markdown Document\nThis is a test document.\n",
        "image.jpg": b"fake image data",  # Binary file
        "subdir/nested.txt": "Nested content inside subdir.\nAnother line here.\n",
        "subdir/code.java": "// Java code\npublic class Test {\n    public static void main(String[] args) {\n        System.out.println(\"Hello\");\n    }\n}\n",
        ".hidden_file": "This is a hidden file.\n",
        ".hidden_dir/hidden.txt": "Hidden directory file.\n",
        "large_file.txt": "x" * 10000 + "\n"  # Larger file for testing
    }

    for rel_path, content in files.items():
        abs_path = os.path.join(tmp_dir, rel_path)
        Path(abs_path).parent.mkdir(parents=True, exist_ok=True)
        
        if isinstance(content, bytes):
            # Write binary file
            with open(abs_path, "wb") as f:
                f.write(content)
        else:
            # Write text file
            with open(abs_path, "w", encoding="utf-8") as f:
                f.write(content)

    yield tmp_dir
    shutil.rmtree(tmp_dir)


@pytest.fixture(autouse=True)
def reset_globals():
    """Reset global variables before each test."""
    STATS.update({
        'total_files': 0,
        'total_lines': 0,
        'total_bytes': 0,
        'code_files': 0,
        'doc_files': 0,
        'media_files': 0,
        'other_files': 0,
        'errors': 0,
        'large_files': 0
    })
    TOP_LINES.clear()
    TOP_SIZE.clear()
    yield


def test_should_process_file(tmp_test_dir):
    """Test file filtering logic."""
    # Test text file should be processed
    txt_file = Path(tmp_test_dir) / "root.txt"
    assert should_process_file(txt_file, False, False, False, None) == True
    
    # Test code file with code_only filter
    py_file = Path(tmp_test_dir) / "config.py"
    assert should_process_file(py_file, False, True, False, None) == True
    
    # Test doc file with doc_only filter  
    md_file = Path(tmp_test_dir) / "document.md"
    assert should_process_file(md_file, True, False, False, None) == True
    
    # Test binary file should not be processed
    jpg_file = Path(tmp_test_dir) / "image.jpg"
    assert should_process_file(jpg_file, False, False, False, None) == False
    
    # Test with extension filter
    assert should_process_file(txt_file, False, False, False, {'.py', '.js'}) == False
    assert should_process_file(py_file, False, False, False, {'.py', '.js'}) == True


def test_cat_file(tmp_test_dir, capsys):
    """Test reading individual file content."""
    file_path = Path(tmp_test_dir) / "root.txt"
    
    # Capture output
    output = io.StringIO()
    cat_file(file_path, output, max_lines=1000)
    
    content = output.getvalue()
    assert "root file" in content
    assert "multiple lines" in content
    assert STATS['total_files'] == 1
    assert STATS['doc_files'] == 1


def test_cat_file_truncation(tmp_test_dir):
    """Test file content truncation."""
    file_path = Path(tmp_test_dir) / "large_file.txt"
    
    output = io.StringIO()
    cat_file(file_path, output, max_lines=5)
    
    content = output.getvalue()
    assert "TRUNCATED" in content
    assert STATS['total_files'] == 1


def test_cat_all_recursive(tmp_test_dir):
    """Test recursive directory processing."""
    output = io.StringIO()
    
    cat_all(
        root=tmp_test_dir,
        include_hidden=False,
        doc_only=False,
        code_only=False,
        media_only=False,
        extensions=None,
        out=output,
        current_only=False,
        max_file_size=10*1024*1024,
        max_lines=1000,
        top_n=5
    )
    
    content = output.getvalue()
    assert "root.txt" in content
    assert "nested.txt" in content
    assert "config.py" in content
    assert STATS['total_files'] >= 5  # Should find multiple files


def test_cat_all_current_only(tmp_test_dir):
    """Test non-recursive directory processing."""
    output = io.StringIO()
    
    cat_all(
        root=tmp_test_dir,
        include_hidden=False,
        doc_only=False,
        code_only=False,
        media_only=False,
        extensions=None,
        out=output,
        current_only=True,
        max_file_size=10*1024*1024,
        max_lines=1000,
        top_n=5
    )
    
    # Should only process files in root directory, not subdir
    assert STATS['total_files'] >= 4  # Files in root, excluding hidden
    output_str = output.getvalue()
    assert "nested.txt" not in output_str  # Should not process subdir files


def test_cat_all_with_filters(tmp_test_dir):
    """Test processing with file type filters."""
    output = io.StringIO()
    
    # Test code-only filter
    cat_all(
        root=tmp_test_dir,
        include_hidden=False,
        doc_only=False,
        code_only=True,
        media_only=False,
        extensions=None,
        out=output,
        current_only=False,
        max_file_size=10*1024*1024,
        max_lines=1000,
        top_n=5
    )
    
    assert STATS['code_files'] >= 2  # Should find .py and .js files
    assert STATS['doc_files'] == 0  # Should not include documents


def test_cat_all_include_hidden(tmp_test_dir):
    """Test processing with hidden files included."""
    output = io.StringIO()
    
    cat_all(
        root=tmp_test_dir,
        include_hidden=True,
        doc_only=False,
        code_only=False,
        media_only=False,
        extensions=None,
        out=output,
        current_only=False,
        max_file_size=10*1024*1024,
        max_lines=1000,
        top_n=5
    )
    
    # Should process more files including hidden ones
    assert STATS['total_files'] >= 7  # Includes hidden files


def test_cat_all_extension_filter(tmp_test_dir):
    """Test processing with custom extension filter."""
    output = io.StringIO()
    
    cat_all(
        root=tmp_test_dir,
        include_hidden=False,
        doc_only=False,
        code_only=False,
        media_only=False,
        extensions={'.txt', '.md'},
        out=output,
        current_only=False,
        max_file_size=10*1024*1024,
        max_lines=1000,
        top_n=5
    )
    
    # Should only process .txt and .md files
    assert STATS['doc_files'] >= 3  # .txt and .md files
    assert STATS['code_files'] == 0  # Should not include code files


def test_get_file_color(tmp_test_dir):
    """Test file color determination."""
    # Test code files
    assert get_file_color(Path(tmp_test_dir) / "config.py") != ""
    assert get_file_color(Path(tmp_test_dir) / "script.js") != ""
    
    # Test document files
    assert get_file_color(Path(tmp_test_dir) / "root.txt") != ""
    assert get_file_color(Path(tmp_test_dir) / "document.md") != ""
    
    # Test media files (should get media color or fallback)
    assert get_file_color(Path(tmp_test_dir) / "image.jpg") != ""


def test_format_size():
    """Test size formatting."""
    assert format_size(0) == "0 B"
    assert format_size(1024) == "1.0 KB"
    assert format_size(1024 * 1024) == "1.0 MB"
    assert "KB" in format_size(1500)
    assert "MB" in format_size(1500000)


def test_is_text_file(tmp_test_dir):
    """Test text file detection."""
    # Text files should return True
    txt_file = Path(tmp_test_dir) / "root.txt"
    assert is_text_file(txt_file) == True
    
    # Code files should return True
    py_file = Path(tmp_test_dir) / "config.py"
    assert is_text_file(py_file) == True
    
    # Binary files should return False
    jpg_file = Path(tmp_test_dir) / "image.jpg"
    assert is_text_file(jpg_file) == False


def test_print_summary(capsys):
    """Test summary output."""
    # Set up some stats
    STATS.update({
        'total_files': 10,
        'total_lines': 1000,
        'total_bytes': 50000,
        'code_files': 5,
        'doc_files': 3,
        'media_files': 1,
        'other_files': 1,
        'errors': 0,
        'large_files': 2
    })
    
    TOP_LINES.extend([(500, "file1.py"), (300, "file2.js"), (200, "file3.txt")])
    TOP_SIZE.extend([(30000, "large_file.bin"), (20000, "big_file.txt")])
    
    print_summary(top_n=3)
    captured = capsys.readouterr()
    
    assert "DEV AUDIT SUMMARY" in captured.out
    assert "Total files processed: 10" in captured.out
    assert "Total lines: 1000" in captured.out
    assert "file1.py" in captured.out
    assert "large_file.bin" in captured.out


def test_invalid_path():
    """Test handling of invalid paths."""
    output = io.StringIO()
    
    cat_all(
        root="/nonexistent/path/that/does/not/exist",
        include_hidden=False,
        doc_only=False,
        code_only=False,
        media_only=False,
        extensions=None,
        out=output,
        current_only=False,
        max_file_size=10*1024*1024,
        max_lines=1000,
        top_n=5
    )
    
    # Should handle gracefully without crashing
    assert STATS['total_files'] == 0


def test_file_permission_error(tmp_test_dir, monkeypatch):
    """Test handling of permission errors."""
    # Mock file operations to simulate permission error
    def mock_open(*args, **kwargs):
        raise PermissionError("Mock permission error")
    
    monkeypatch.setattr("builtins.open", mock_open)
    
    file_path = Path(tmp_test_dir) / "root.txt"
    output = io.StringIO()
    
    cat_file(file_path, output, max_lines=1000)
    
    assert STATS['errors'] == 1
    assert STATS['total_files'] == 0


def test_top_lists_ordering(tmp_test_dir):
    """Test that top files lists are properly ordered."""
    # Process multiple files to populate top lists
    output = io.StringIO()
    
    cat_all(
        root=tmp_test_dir,
        include_hidden=False,
        doc_only=False,
        code_only=False,
        media_only=False,
        extensions=None,
        out=output,
        current_only=True,  # Just process root directory for simplicity
        max_file_size=10*1024*1024,
        max_lines=1000,
        top_n=3
    )
    
    # Check that lists are properly sorted
    if TOP_LINES:
        lines = [item[0] for item in TOP_LINES]
        assert lines == sorted(lines, reverse=True)
    
    if TOP_SIZE:
        sizes = [item[0] for item in TOP_SIZE]
        assert sizes == sorted(sizes, reverse=True)
