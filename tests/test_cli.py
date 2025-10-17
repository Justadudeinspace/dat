#!/usr/bin/env python3
"""
tests/test_cli.py

End-to-end CLI tests for the `dat` Dev Audit Tool.

These tests:
- Locate the `dat` executable (dat or dat.py in repo root)
- Create temporary directories & sample files
- Invoke `dat` via subprocess
- Assert expected stdout / output file behavior

Run with:
    pytest -q
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
import textwrap
import platform

import pytest

# ---------- Helper functions ----------

def find_dat_executable(repo_root: Path) -> Path:
    """
    Look for an executable 'dat' or a 'dat.py' script in the repository root.
    Returns the path to the executable to run (may be a script file).
    """
    candidates = [
        repo_root / "dat",
        repo_root / "dat.py",
        repo_root / "src" / "dat",      # support alternate layouts
        repo_root / "src" / "dat.py",
    ]
    for p in candidates:
        if p.exists():
            return p
    raise FileNotFoundError("Could not find 'dat' or 'dat.py' in repo root. Ensure tests run from repository root.")


def run_dat(exe_path: Path, args, cwd=None, env=None, timeout=30):
    """
    Run dat with the provided args and return CompletedProcess.
    If exe_path is a .py file, run `sys.executable exe_path ...`
    Otherwise run the file directly (it is expected to be executable).
    """
    if exe_path.suffix == ".py":
        cmd = [sys.executable, str(exe_path)] + list(args)
    else:
        cmd = [str(exe_path)] + list(args)

    run_env = os.environ.copy()
    if env:
        run_env.update(env)

    # Ensure consistent environment for testing
    run_env['NO_COLOR'] = '1'  # Disable colors for consistent output
    run_env['PYTHONIOENCODING'] = 'utf-8'

    proc = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=cwd,
        env=run_env,
        timeout=timeout,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    return proc


def create_sample_project(tmp_path: Path) -> Path:
    """
    Create a comprehensive sample project layout matching dat's capabilities.
    
    Structure:
    /project
      /src
        main.py
        utils.js
        config.ini
      /docs
        README.md
        manual.txt
      /static
        image.jpg (binary)
        style.css
      /subdir
        nested.py
        data.json
      .hidden_file
      .hidden_dir/.config
      large_file.txt (many lines)
      custom.foo
      binary.dat
    """
    root = tmp_path / "project"
    src = root / "src"
    docs = root / "docs"
    static = root / "static"
    subdir = root / "subdir"
    hidden_dir = root / ".hidden_dir"
    
    # Create directories
    for dir_path in [src, docs, static, subdir, hidden_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)

    # Code files
    (src / "main.py").write_text(textwrap.dedent("""\
        # main.py - Primary application entry point
        import sys
        
        def main():
            '''Main function that prints greeting'''
            print("Hello from main!")
            return 0
            
        if __name__ == "__main__":
            sys.exit(main())
    """))

    (src / "utils.js").write_text(textwrap.dedent("""\
        // utils.js - JavaScript utility functions
        function capitalize(str) {
            return str.charAt(0).toUpperCase() + str.slice(1);
        }
        
        module.exports = { capitalize };
    """))

    (src / "config.ini").write_text(textwrap.dedent("""\
        [database]
        host = localhost
        port = 5432
        name = myapp
        
        [settings]
        debug = true
        timeout = 30
    """))

    # Document files
    (docs / "README.md").write_text(textwrap.dedent("""\
        # Project README
        
        This is a sample project for testing the Dev Audit Tool.
        
        ## Features
        - Feature one
        - Feature two
        - Feature three
    """))

    (docs / "manual.txt").write_text(textwrap.dedent("""\
        USER MANUAL
        ===========
        
        This is a text-based manual for the application.
        It contains multiple lines of documentation.
    """))

    # Static files
    (static / "style.css").write_text(textwrap.dedent("""\
        /* Main stylesheet */
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
    """))

    # Create fake binary image data
    (static / "image.jpg").write_bytes(b'\xff\xd8\xff\xe0' + b'FAKE_JPEG_DATA' * 100)

    # Nested files
    (subdir / "nested.py").write_text(textwrap.dedent("""\
        # nested.py - Deeply nested Python module
        def nested_function():
            '''A function in a nested directory'''
            return "nested result"
    """))

    (subdir / "data.json").write_text(textwrap.dedent("""\
        {
            "project": "dev-audit-tool",
            "version": "1.0.0",
            "files": ["main.py", "utils.js", "README.md"]
        }
    """))

    # Hidden files
    (root / ".hidden_file").write_text("This is a hidden configuration file\n")
    (hidden_dir / ".config").write_text("hidden_dir_config=value\n")

    # Large file for truncation testing (500 lines)
    large_file = root / "large_file.txt"
    with open(large_file, "w", encoding="utf-8") as f:
        for i in range(1, 501):
            f.write(f"This is line {i:03d} of the large test file for truncation testing.\n")

    # Custom extension file
    (root / "custom.foo").write_text("custom file with .foo extension\ncontent line 2\ncontent line 3\n")

    # Binary file (should be skipped)
    (root / "binary.dat").write_bytes(b'\x00\x01\x02\x03' * 1000)

    return root


# ---------- Fixtures ----------

@pytest.fixture(scope="module")
def repo_root():
    """Find the repository root containing the dat executable."""
    here = Path(__file__).resolve().parent
    # climb up until we find a dat or dat.py or hit filesystem root
    candidate = here
    for _ in range(6):
        if (candidate / "dat").exists() or (candidate / "dat.py").exists():
            return candidate
        candidate = candidate.parent
    # fallback to current working directory
    return Path.cwd()


@pytest.fixture
def sample_project(tmp_path):
    """Create a comprehensive sample project for testing."""
    return create_sample_project(tmp_path)


@pytest.fixture
def dat_executable(repo_root):
    """Get the dat executable path."""
    return find_dat_executable(repo_root)


# ---------- Tests ----------

def test_version_shows_version_info(dat_executable):
    """Test --version flag shows proper version information."""
    proc = run_dat(dat_executable, ["--version"])
    assert proc.returncode == 0, f"stderr:\n{proc.stderr}"
    output = proc.stdout + proc.stderr
    
    # Check for version information patterns
    assert "dat - Dev Audit Tool" in output or "Dev Audit Tool" in output
    assert "Platform:" in output
    assert "Python:" in output
    assert "Install path:" in output


def test_basic_audit_current_directory(dat_executable, sample_project):
    """Test basic audit functionality in current directory."""
    proc = run_dat(dat_executable, [str(sample_project)])
    assert proc.returncode == 0, f"stderr:\n{proc.stderr}"
    output = proc.stdout
    
    # Should find and display content from various file types
    assert "main.py - Primary application entry point" in output
    assert "utils.js - JavaScript utility functions" in output
    assert "Project README" in output
    assert "USER MANUAL" in output
    assert "nested.py - Deeply nested Python module" in output
    assert "custom file with .foo extension" in output


def test_code_only_filter(dat_executable, sample_project):
    """Test -c/--code flag filters to code files only."""
    proc = run_dat(dat_executable, [str(sample_project), "-c"])
    assert proc.returncode == 0, f"stderr:\n{proc.stderr}"
    output = proc.stdout
    
    # Should contain code files
    assert "main.py" in output
    assert "utils.js" in output
    assert "nested.py" in output
    assert "config.ini" in output
    assert "style.css" in output
    assert "data.json" in output
    
    # Should NOT contain document files
    assert "Project README" not in output
    assert "USER MANUAL" not in output


def test_docs_only_filter(dat_executable, sample_project):
    """Test -d/--docs flag filters to document files only."""
    proc = run_dat(dat_executable, [str(sample_project), "-d"])
    assert proc.returncode == 0, f"stderr:\n{proc.stderr}"
    output = proc.stdout
    
    # Should contain document files
    assert "Project README" in output
    assert "USER MANUAL" in output
    
    # Should NOT contain code files
    assert "main.py" not in output
    assert "utils.js" not in output
    assert "nested.py" not in output


def test_custom_extension_filter(dat_executable, sample_project):
    """Test -e/--ext flag with custom file extensions."""
    proc = run_dat(dat_executable, [str(sample_project), "-e", "foo,json"])
    assert proc.returncode == 0, f"stderr:\n{proc.stderr}"
    output = proc.stdout
    
    # Should contain custom extension files
    assert "custom file with .foo extension" in output
    assert '"project": "dev-audit-tool"' in output
    
    # Should NOT contain other file types
    assert "main.py" not in output
    assert "Project README" not in output


def test_max_lines_truncation(dat_executable, sample_project):
    """Test --max-lines truncates large files properly."""
    proc = run_dat(dat_executable, [str(sample_project), "--max-lines", "10"])
    assert proc.returncode == 0, f"stderr:\n{proc.stderr}"
    output = proc.stdout
    
    # Should indicate truncation
    assert "TRUNCATED" in output or "truncated" in output.lower()
    
    # Should contain first lines but not very high line numbers
    assert "line 001" in output
    assert "line 500" not in output  # File has 500 lines, truncated to 10


def test_output_to_file(dat_executable, sample_project, tmp_path):
    """Test -o/--output writes to specified file."""
    out_file = tmp_path / "audit_report.txt"
    proc = run_dat(dat_executable, [str(sample_project), "-o", str(out_file)])
    assert proc.returncode == 0, f"stderr:\n{proc.stderr}"
    
    # Verify output file was created and contains expected content
    assert out_file.exists()
    content = out_file.read_text(encoding="utf-8")
    assert "main.py" in content
    assert "Project README" in content
    assert "nested.py" in content


def test_folder_flag_no_recursion(dat_executable, sample_project):
    """Test -f/--folder flag prevents recursion."""
    proc = run_dat(dat_executable, [str(sample_project), "-f"])
    assert proc.returncode == 0, f"stderr:\n{proc.stderr}"
    output = proc.stdout
    
    # Should contain top-level files
    assert "large_file.txt" in output or "large_file.txt" in (proc.stdout + proc.stderr)
    assert "custom.foo" in output
    
    # Should NOT contain nested files (these are in subdirectories)
    assert "nested.py" not in output
    assert "README.md" not in output


def test_include_hidden_files(dat_executable, sample_project):
    """Test -a/--all flag includes hidden files."""
    proc = run_dat(dat_executable, [str(sample_project), "-a"])
    assert proc.returncode == 0, f"stderr:\n{proc.stderr}"
    output = proc.stdout
    
    # Should contain hidden file content
    assert "hidden configuration file" in output
    assert "hidden_dir_config=value" in output


def test_exclude_hidden_files_by_default(dat_executable, sample_project):
    """Test hidden files are excluded by default."""
    proc = run_dat(dat_executable, [str(sample_project)])
    assert proc.returncode == 0, f"stderr:\n{proc.stderr}"
    output = proc.stdout
    
    # Should NOT contain hidden file content by default
    assert "hidden configuration file" not in output
    assert "hidden_dir_config=value" not in output


def test_top_n_summary(dat_executable, sample_project):
    """Test --top-n affects summary output."""
    proc = run_dat(dat_executable, [str(sample_project), "--top-n", "3"])
    assert proc.returncode == 0, f"stderr:\n{proc.stderr}"
    output = proc.stdout + proc.stderr
    
    # Summary should mention top files
    assert "Top 3" in output or "Top" in output
    assert "files by lines" in output or "lines" in output
    assert "files by size" in output or "size" in output


def test_no_bootstrap_flag(dat_executable, sample_project):
    """Test --no-bootstrap flag prevents installation behavior."""
    proc = run_dat(dat_executable, [str(sample_project), "--no-bootstrap"])
    assert proc.returncode == 0, f"stderr:\n{proc.stderr}"
    output = proc.stdout + proc.stderr
    
    # Should run successfully without bootstrap messages
    assert "BOOTSTRAP" not in output
    assert "Total files processed" in output or "main.py" in output


def test_media_filter(dat_executable, sample_project):
    """Test -m/--media flag for media files (should skip binary files)."""
    proc = run_dat(dat_executable, [str(sample_project), "-m"])
    assert proc.returncode == 0, f"stderr:\n{proc.stderr}"
    output = proc.stdout + proc.stderr
    
    # Media files should be skipped (binary detection)
    # The summary should show media_files count but no content for binary files
    assert "media_files: 0" in output or "Media: 0" in output or "Skipped large files" in output


def test_summary_statistics(dat_executable, sample_project):
    """Test that summary statistics are properly displayed."""
    proc = run_dat(dat_executable, [str(sample_project)])
    assert proc.returncode == 0, f"stderr:\n{proc.stderr}"
    output = proc.stdout + proc.stderr
    
    # Check for summary section
    assert "DEV AUDIT SUMMARY" in output
    assert "Total files processed:" in output
    assert "Total lines:" in output
    assert "Total size:" in output
    assert "Code files:" in output
    assert "Docs:" in output


def test_error_handling_invalid_path(dat_executable):
    """Test graceful handling of non-existent paths."""
    proc = run_dat(dat_executable, ["/nonexistent/path/that/does/not/exist"])
    # Should handle gracefully - might return 0 or non-zero, but shouldn't crash
    assert "Error:" in (proc.stdout + proc.stderr) or "does not exist" in (proc.stdout + proc.stderr)


def test_combination_filters(dat_executable, sample_project):
    """Test combining multiple filters."""
    proc = run_dat(dat_executable, [str(sample_project), "-c", "-f", "-e", "py"])
    assert proc.returncode == 0, f"stderr:\n{proc.stderr}"
    output = proc.stdout
    
    # Should only show Python files in current directory
    # (sample_project root has no .py files, all are in src/ and subdir/)
    # So with -f, should find no Python files
    assert "main.py" not in output  # This is in src/ directory
    assert "nested.py" not in output  # This is in subdir/ directory


def test_binary_files_skipped(dat_executable, sample_project):
    """Test that binary files are properly skipped."""
    proc = run_dat(dat_executable, [str(sample_project)])
    assert proc.returncode == 0, f"stderr:\n{proc.stderr}"
    output = proc.stdout
    
    # Binary file content should not appear
    assert "FAKE_JPEG_DATA" not in output
    assert "\x00\x01\x02\x03" not in output


# ---------- Platform-specific tests ----------

@pytest.mark.skipif(platform.system() != "Windows", reason="Windows-specific test")
def test_windows_path_handling(dat_executable, sample_project):
    """Test Windows path handling."""
    # Use Windows-style path arguments
    proc = run_dat(dat_executable, [str(sample_project).replace('/', '\\')])
    assert proc.returncode == 0, f"stderr:\n{proc.stderr}"
    assert "main.py" in proc.stdout


# ---------- End of tests ----------
