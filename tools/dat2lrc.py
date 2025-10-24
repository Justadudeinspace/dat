#!/usr/bin/env python3
"""
dat2lrc — ultra-simple exporter:
Turn a folder into a single LRC schema.

Usage:
  dat2lrc.py -r ./repo -o exported.lrc
  dat2lrc.py -r ./repo -o exported.lrc -i ".git __pycache__ .venv node_modules"
  dat2lrc.py -r ./repo --dry-run
  dat2lrc.py --platform-info

Rules:
- Text & small files (<= 64 KB and <= 400 lines) → inline with heredoc.
- Everything else → @copy <source> <dest>.
- Schema keeps directory structure using /sections.

This tool is standalone. Later you can wire it into `dat` as --export-schema.
"""

from __future__ import annotations
import argparse
import os
import sys
import mimetypes
import platform
import stat
from pathlib import Path
from typing import Set, List, Dict, Tuple, Optional

# Cross-platform defaults
DEFAULT_IGNORES = {
    ".git", "__pycache__", ".DS_Store", ".venv", "node_modules", 
    ".mypy_cache", ".pytest_cache", ".coverage", "*.pyc", "*.pyo",
    "Thumbs.db", "ehthumbs.db", "Desktop.ini", ".Spotlight-V100",
    ".Trashes", "._*", ".fseventsd"
}
INLINE_MAX_BYTES = 64 * 1024  # 64KB
INLINE_MAX_LINES = 400
BINARY_EXTENSIONS = {
    '.exe', '.dll', '.so', '.dylib', '.bin', '.app', '.dmg', '.pkg',
    '.deb', '.rpm', '.msi', '.zip', '.tar', '.gz', '.7z', '.rar',
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.ico', '.svg',
    '.mp3', '.mp4', '.avi', '.mov', '.wav', '.flac', '.pdf', '.doc',
    '.docx', '.xls', '.xlsx', '.ppt', '.pptx'
}

# Platform detection
IS_WINDOWS = platform.system().lower() == "windows"
IS_LINUX = platform.system().lower() == "linux"
IS_MACOS = platform.system().lower() == "darwin"
IS_ANDROID = "android" in platform.platform().lower()
IS_TERMUX = IS_ANDROID and "com.termux" in os.environ.get("PREFIX", "")


def print_platform_info() -> None:
    """Print platform information for debugging."""
    info = [
        f"Platform: {platform.platform()}",
        f"System: {platform.system()}",
        f"Python: {platform.python_version()}",
        f"Windows: {IS_WINDOWS}",
        f"Linux: {IS_LINUX}",
        f"macOS: {IS_MACOS}",
        f"Android: {IS_ANDROID}",
        f"Termux: {IS_TERMUX}",
        f"Current Dir: {Path.cwd()}",
        f"Executable: {sys.executable}",
    ]
    print("\n".join(info))


def is_text_file(p: Path, sniff: int = 4096) -> bool:
    """
    Enhanced text file detection with multiple strategies:
    1. Check file extension against known binary types
    2. Look for null bytes (definitive binary indicator)
    3. Use MIME type detection
    4. Analyze character distribution
    """
    # Check extension first (fast path)
    if p.suffix.lower() in BINARY_EXTENSIONS:
        return False
    
    try:
        # Get file size
        stat_info = p.stat()
        if stat_info.st_size == 0:
            return True  # Empty files are considered text
            
        # Read sample for analysis
        with p.open('rb') as f:
            sample = f.read(sniff)
            
        if not sample:
            return True
            
        # Null byte check (definitive binary indicator)
        if b'\x00' in sample:
            return False
            
        # MIME type detection
        mt, _ = mimetypes.guess_type(str(p))
        if mt:
            if mt.startswith('text/'):
                return True
            if mt in ('application/xml', 'application/json', 'application/javascript'):
                return True
            if mt.startswith('application/') and 'script' in mt:
                return True
                
        # Character distribution analysis
        # Count control characters (excluding common whitespace: \t, \n, \r)
        control_chars = 0
        printable_chars = 0
        for byte in sample:
            if byte < 32 and byte not in (9, 10, 13):  # Not tab, LF, or CR
                control_chars += 1
            elif 32 <= byte <= 126:  # Printable ASCII
                printable_chars += 1
            elif byte > 126:  # Extended ASCII / UTF-8
                printable_chars += 1
                
        total_chars = len(sample)
        if total_chars == 0:
            return True
            
        # If >5% control characters or <70% printable, likely binary
        control_ratio = control_chars / total_chars
        printable_ratio = printable_chars / total_chars
        
        return control_ratio < 0.05 and printable_ratio > 0.7
        
    except (OSError, IOError, PermissionError):
        return False


def read_text(p: Path) -> str:
    """
    Read text file with automatic encoding detection and fallback.
    """
    encodings = [
        'utf-8',
        'utf-8-sig',  # Handle BOM
        'utf-16',
        'utf-16-le',
        'utf-16-be',
        'latin-1',
        'cp1252',
        'iso-8859-1',
        'ascii'
    ]
    
    for encoding in encodings:
        try:
            return p.read_text(encoding=encoding)
        except (UnicodeDecodeError, UnicodeError):
            continue
            
    # Final fallback with replacement
    try:
        return p.read_text(encoding='utf-8', errors='replace')
    except Exception as e:
        return f"# ERROR: Could not read file {p}: {e}\n"


def should_ignore(path: Path, ignore_patterns: Set[str], root: Path) -> bool:
    """
    Enhanced pattern matching for ignore rules.
    Supports:
    - Exact filename matches
    - Directory name matches
    - Wildcard patterns in filenames
    - Path segment matching
    """
    if not ignore_patterns:
        return False
        
    path_str = str(path)
    name = path.name
    parts = set(path.parts)
    rel_path = path.relative_to(root) if path.is_relative_to(root) else path
    
    for pattern in ignore_patterns:
        pattern = pattern.strip()
        if not pattern:
            continue
            
        # Exact name match
        if name == pattern:
            return True
            
        # Directory marker (ends with /)
        if pattern.endswith('/') and path.is_dir() and name == pattern[:-1]:
            return True
            
        # Wildcard matching in current directory
        if '*' in pattern or '?' in pattern:
            import fnmatch
            if fnmatch.fnmatch(name, pattern):
                return True
            if fnmatch.fnmatch(str(rel_path), pattern):
                return True
                
        # Path segment matching
        if pattern in parts:
            return True
            
        # Substring in full path (conservative)
        if pattern in path_str:
            # Only return True if this looks like a intentional path match
            if f"/{pattern}/" in f"/{path_str}/" or path_str.endswith(f"/{pattern}"):
                return True
                
    return False


def get_relative_path(child: Path, base: Path) -> str:
    """
    Get relative path with proper cross-platform handling.
    """
    try:
        if child == base:
            return "."
        relative = child.relative_to(base)
        return str(relative).replace("\\", "/")
    except ValueError:
        # Fallback for paths not relative to base
        return str(child).replace("\\", "/")


def choose_heredoc_marker(text: str, used_markers: Set[str]) -> str:
    """
    Choose a unique heredoc marker that doesn't conflict with content.
    """
    base_markers = ["EOF", "END", "EOT", "DOC", "MARKER"]
    
    for base in base_markers:
        marker = base
        counter = 1
        while marker in used_markers or marker in text:
            marker = f"{base}_{counter}"
            counter += 1
        used_markers.add(marker)
        return marker
        
    # Fallback
    marker = "HEREDOC"
    counter = 1
    while marker in used_markers or marker in text:
        marker = f"HEREDOC_{counter}"
        counter += 1
    used_markers.add(marker)
    return marker


def detect_executable_files(root: Path) -> Set[Path]:
    """
    Detect executable files that should get @chmod directives.
    """
    executables = set()
    
    try:
        for file_path in root.rglob("*"):
            if file_path.is_file():
                try:
                    # Unix-like systems: check execute permission
                    if not IS_WINDOWS:
                        mode = file_path.stat().st_mode
                        if mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH):
                            executables.add(file_path)
                    
                    # Windows & Unix: check file extensions and shebangs
                    if file_path.suffix.lower() in ('.sh', '.py', '.pl', '.rb', '.bash'):
                        executables.add(file_path)
                    elif file_path.name in ('Makefile', 'makefile'):
                        continue  # Makefiles aren't executable by themselves
                    else:
                        # Check for shebang
                        try:
                            with file_path.open('rb') as f:
                                first_line = f.readline(100)
                                if first_line.startswith(b'#!'):
                                    executables.add(file_path)
                        except (IOError, UnicodeDecodeError):
                            pass
                            
                except (OSError, PermissionError):
                    continue
                    
    except (OSError, PermissionError):
        pass  # Can't traverse some directories
        
    return executables


def export_folder(
    root: Path, 
    out_path: Path, 
    ignores: Set[str], 
    dry_run: bool, 
    force: bool,
    verbose: bool = False
) -> None:
    """
    Main export function that converts folder structure to LRC schema.
    """
    if not root.exists():
        print(f"[ERROR] Root directory not found: {root}", file=sys.stderr)
        sys.exit(2)
        
    if not root.is_dir():
        print(f"[ERROR] Root path is not a directory: {root}", file=sys.stderr)
        sys.exit(2)

    schema_dir = out_path.parent.resolve()
    lines: List[str] = []
    
    # Schema header with metadata
    lines.extend([
        "# =========================================================",
        f"# Generated by dat2lrc v1.0.0",
        f"# Source: {root}",
        f"# Timestamp: {platform.node()} @ {platform.system()}",
        "# =========================================================",
        "",
        f"# Project: {root.name}",
        f"# Description: Exported from {root}",
        "# Version: 0.1.0",
        "# Generator: dat2lrc",
        "",
    ])
    
    # Add ignore patterns
    if ignores:
        lines.append("@ignore " + " ".join(sorted(ignores)))
        lines.append("")

    # Build directory structure map
    dir_map: Dict[Path, List[Path]] = {}
    executable_files = detect_executable_files(root)
    
    if verbose:
        print(f"[INFO] Scanning {root}...")
        
    try:
        for dirpath, dirnames, filenames in os.walk(root):
            current_dir = Path(dirpath)
            
            # Filter directories to traverse
            dirnames[:] = [
                dn for dn in dirnames 
                if not should_ignore(current_dir / dn, ignores, root)
            ]
            
            # Skip ignored directories
            if should_ignore(current_dir, ignores, root):
                continue
                
            # Collect non-ignored files
            files = []
            for filename in filenames:
                file_path = current_dir / filename
                if not should_ignore(file_path, ignores, root):
                    files.append(file_path)
                    
            if files or current_dir != root:  # Include directories even if empty
                dir_map[current_dir] = sorted(files)
                
    except (OSError, PermissionError) as e:
        print(f"[WARNING] Could not traverse some directories: {e}", file=sys.stderr)

    # Order sections by depth and name
    sections = sorted(
        dir_map.keys(), 
        key=lambda p: (len(p.relative_to(root).parts) if p.is_relative_to(root) else 0, str(p).lower())
    )

    used_markers: Set[str] = set()
    stats = {
        'files_inline': 0,
        'files_copy': 0,
        'directories': 0,
        'executables': 0
    }

    if verbose:
        print(f"[INFO] Processing {len(sections)} directories...")

    for section in sections:
        rel_section = get_relative_path(section, root)
        if rel_section == ".":
            lines.append("/")
        else:
            lines.append(f"/{rel_section}")
        stats['directories'] += 1

        for file_path in dir_map[section]:
            rel_file = get_relative_path(file_path, section)
            
            try:
                file_size = file_path.stat().st_size
                is_executable = file_path in executable_files
                
                # Try inline for text files under size/line limits
                if (is_text_file(file_path) and 
                    file_size <= INLINE_MAX_BYTES and 
                    file_size > 0):  # Skip empty files for inline
                    
                    try:
                        content = read_text(file_path)
                        line_count = content.count('\n') + (1 if content and not content.endswith('\n') else 0)
                        
                        if line_count <= INLINE_MAX_LINES:
                            marker = choose_heredoc_marker(content, used_markers)
                            lines.append(f"  {rel_file} <<{marker}")
                            lines.extend(content.splitlines())
                            lines.append(marker)
                            
                            # Add chmod for executable files
                            if is_executable and not IS_WINDOWS:
                                lines.append(f"  @chmod {rel_file} +x")
                                stats['executables'] += 1
                                
                            stats['files_inline'] += 1
                            continue
                    except (IOError, OSError, UnicodeError) as e:
                        if verbose:
                            print(f"[WARNING] Could not read {file_path} for inline: {e}")

                # Fallback to @copy
                try:
                    # Calculate relative path from schema location
                    if schema_dir in file_path.parents:
                        src_path = get_relative_path(file_path, schema_dir)
                    else:
                        # Use absolute path if not relative to schema dir
                        src_path = str(file_path)
                        
                    dst_path = get_relative_path(file_path, root)
                    lines.append(f"  @copy {src_path} {dst_path}")
                    
                    # Add chmod for executable files
                    if is_executable and not IS_WINDOWS:
                        lines.append(f"  @chmod {dst_path} +x")
                        stats['executables'] += 1
                        
                    stats['files_copy'] += 1
                    
                except (ValueError, OSError) as e:
                    if verbose:
                        print(f"[WARNING] Could not process {file_path}: {e}")
                    lines.append(f"  # ERROR: Could not process {rel_file}")

            except (OSError, PermissionError) as e:
                if verbose:
                    print(f"[WARNING] Could not access {file_path}: {e}")
                lines.append(f"  # ERROR: Could not access {rel_file}")

        lines.append("")  # Empty line between sections

    # Add footer with statistics
    lines.extend([
        "# =========================================================",
        "# Export Statistics:",
        f"#   Directories: {stats['directories']}",
        f"#   Files (inline): {stats['files_inline']}",
        f"#   Files (copy): {stats['files_copy']}",
        f"#   Executables: {stats['executables']}",
        f"#   Total Files: {stats['files_inline'] + stats['files_copy']}",
        "# =========================================================",
        ""
    ])

    out_text = "\n".join(lines).rstrip() + "\n"

    if dry_run:
        print(out_text)
        if verbose:
            print(f"\n[DRY RUN] Would create schema with:")
            print(f"  - {stats['directories']} directories")
            print(f"  - {stats['files_inline']} inline files")
            print(f"  - {stats['files_copy']} copy files")
            print(f"  - {stats['executables']} executable files")
        return

    if out_path.exists() and not force:
        print(f"[SKIP] Output file exists: {out_path} (use --force to overwrite)")
        return

    try:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(out_text, encoding="utf-8")
        print(f"[SUCCESS] Schema exported to: {out_path}")
        print(f"[STATS]   Directories: {stats['directories']}, " +
              f"Files: {stats['files_inline']} (inline) + {stats['files_copy']} (copy), " +
              f"Executables: {stats['executables']}")
              
    except (IOError, OSError, PermissionError) as e:
        print(f"[ERROR] Could not write output file {out_path}: {e}", file=sys.stderr)
        sys.exit(1)


def parse_ignore_patterns(ignore_arg: str) -> Set[str]:
    """Parse ignore patterns from command line argument."""
    if not ignore_arg:
        return set()
        
    # Split by space or comma, strip whitespace, filter empty
    patterns = set()
    for chunk in ignore_arg.replace(",", " ").split():
        pattern = chunk.strip()
        if pattern:
            patterns.add(pattern)
            
    return patterns


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Export a folder structure as a single LRC schema file.",
        epilog="""
Examples:
  dat2lrc.py -r ./myproject -o project.lrc
  dat2lrc.py -r ./repo -o exported.lrc -i ".git node_modules *.pyc"
  dat2lrc.py -r ./repo --dry-run --verbose
  dat2lrc.py --platform-info

File Handling:
  - Text files <= 64KB and <= 400 lines → included inline
  - Other files → referenced with @copy directives
  - Executable files get @chmod +x directives (Unix-like systems)
  - Binary files are always handled with @copy
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "-r", "--root", 
        default=".", 
        help="Root folder to export (default: current directory)"
    )
    parser.add_argument(
        "-o", "--out", 
        default="exported.lrc", 
        help="Output schema file path (default: exported.lrc)"
    )
    parser.add_argument(
        "-i", "--ignore", 
        default="", 
        help="Space- or comma-separated patterns to ignore"
    )
    parser.add_argument(
        "-n", "--dry-run", 
        action="store_true", 
        help="Print schema to stdout without writing file"
    )
    parser.add_argument(
        "-f", "--force", 
        action="store_true", 
        help="Overwrite output file if it exists"
    )
    parser.add_argument(
        "-v", "--verbose", 
        action="store_true", 
        help="Enable verbose output"
    )
    parser.add_argument(
        "--platform-info", 
        action="store_true", 
        help="Show platform information and exit"
    )
    
    args = parser.parse_args()

    # Handle platform info
    if args.platform_info:
        print_platform_info()
        return

    # Validate and resolve paths
    try:
        root = Path(args.root).resolve()
        out_path = Path(args.out).resolve()
    except Exception as e:
        print(f"[ERROR] Invalid path: {e}", file=sys.stderr)
        sys.exit(1)

    # Parse ignore patterns
    extra_ignores = parse_ignore_patterns(args.ignore)
    ignores = DEFAULT_IGNORES.union(extra_ignores)

    if args.verbose:
        print(f"[CONFIG] Root: {root}")
        print(f"[CONFIG] Output: {out_path}")
        print(f"[CONFIG] Ignore patterns: {sorted(ignores)}")
        print(f"[CONFIG] Dry run: {args.dry_run}")
        print(f"[CONFIG] Force: {args.force}")

    # Perform export
    try:
        export_folder(root, out_path, ignores, args.dry_run, args.force, args.verbose)
    except KeyboardInterrupt:
        print("\n[INFO] Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Export failed: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
