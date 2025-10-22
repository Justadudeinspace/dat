<p align="center">
<img src="./docs/assets/dat-logo-green.png" alt="DAT v2.2.0" width="600">
</p>

# Dev Audit Tool (`dat`) - v2.2.0-Stable

> - Author: ~JADIS | Justadudeinspace
> - Updated by: GPT-5, Deepseek AI, & Gemini 2.0 Flash

A comprehensive `developer audit tool` that prints the contents of files in a directory and its subdirectories, with optional filters for code, documentation, or media files. It now supports PDF output, single file processing, enhanced ignore patterns, and cross-platform compatibility including native Android/Termux detection.

---

## Features

- Prints contents of all files in a directory and subdirectories
- **NEW**: Single file processing with automatic extension resolution
- **NEW**: PDF report generation with formatted output
- Filter by file type: `code`, `docs`, `media`, or custom extensions
- Limit the number of lines displayed per file
- Skip large files to save time
- Include hidden files (dotfiles)
- Optionally print current folder only (no recursion)
- Output results to text, markdown, or PDF files
- Display top files by size or line count
- **ENHANCED**: Robust ignore patterns with comma/space support
- Works cross-platform: Linux, macOS, Windows, Android/Termux (with automatic detection)
- Supports automatic bootstrap installation

---

## Installation

1. Clone Repo

```bash
git clone https://github.com/Justadudeinspace/dat.git
cd dat
```

2. Install Deps

```bash
chmod +x install_deps.sh
./install_deps.sh
```

3. Run Bootstrap Installer First-Run

```bash
chmod +x dat
python3 dat
```

On Windows, you may need to restart your terminal to apply PATH changes.

Optional: Skip bootstrap with `--no-bootstrap`.

---

## Usage

Print the contents of files in a directory, recursively by default:

```bash
# Print all files in current directory and subdirectories
dat
```

---

## Single File Processing (NEW)

```bash
# Print single file to terminal (auto-resolves extensions)
dat -s filename
dat --single filename

# Process single file to output file
dat filename -o output.txt
dat filename -o output.pdf

# Examples with extension resolution
dat -s dat_pdf          # Finds dat_pdf.py, dat_pdf.sh, etc.
dat dat_pdf -o audit.md # Single file to markdown
dat dat_pdf -o audit.pdf # Single file to PDF
```

---

## Filter by File Type

```bash
# Only code files
dat -c

# Only documentation files (markdown, txt, pdf, etc.)
dat -d

# Only media files (images, audio, video)
dat -m

# Custom extensions (both formats supported)
dat -e py,js,html
dat -e .py,.js,.html
```

---

## Ignore Patterns (ENHANCED)

```bash
# Ignore patterns with spaces or commas
dat -i .pyc __pycache__ .git
dat -i ".pyc,__pycache__,.git,node_modules"

# Alternative flag -I also works
dat -I .pyc __pycache__ .git
```

---

##Folder Options

```bash
# Only current folder, no recursion
dat -f

# Include hidden files
dat -a
```

---

## Output Options

```bash
# Output to text file
dat -o audit.txt

# Output to markdown
dat -o audit.md

# Output to PDF (requires reportlab)
dat -o report.pdf

# Combine with filters
dat -c -o code_report.pdf
```

---

## Advanced Options

```bash
# Limit number of lines displayed per file
dat --max-lines 200

# Limit maximum file size (default 10MB)
dat --max-size 5242880

# Show top N files by lines or size
dat --top-n 10

# Skip automatic bootstrap/install
dat --no-bootstrap

# Show version and platform info
dat --version
```

---

## Example Commands

```bash
# Print all code files in project recursively, limit lines to 500, include hidden files, output to PDF
dat /path/to/project -c -a --max-lines 500 -o code_report.pdf

# Print all files with specific extensions in current folder only
dat -f -e py,txt,md

# Print media files under a directory without recursion
dat /path/to/media -m -f

# Single file processing with automatic extension resolution
dat -s main_script    # Finds main_script.py, main_script.sh, etc.
dat config_file -o config_audit.pdf

# Complex ignore patterns
dat -i ".pyc,__pycache__,.git,node_modules,.pytest_cache" -o clean_audit.txt
```

---

## Configuration

`dat` optionally reads settings from a configuration file located at:

```
~/.datconfig
```

You can customize file types, top file counts, line limits, file size limits, and more.

Full Example

```config
[Settings]
# Number of top files to display by lines or size
top_n = 10

# Maximum number of lines to display per file
max_lines = 1000

# Maximum file size to process (in bytes)
max_size = 10485760  # 10 MB

[FileTypes]
# File extensions considered as documentation files
doc_extensions = .md,.txt,.rst,.pdf,.doc,.docx,.odt,.tex,.rtf

# File extensions considered as code files
code_extensions = .py,.js,.jsx,.java,.cpp,.c,.h,.hpp,.cs,.html,.htm,.css,.scss,.sass,.rb,.php,.go,.swift,.kt,.ts,.tsx,.rs,.sh,.bash,.zsh,.lua,.json,.xml,.yaml,.yml,.pl,.r,.dart,.m,.scala,.hs,.cob,.fs,.groovy,.vb,.tcl,.sql,.config,.ini,.toml,.cfg,.conf,.ps1,.bat,.cmd,.vbs,.asm,.s,.nim,.jl,.ex,.exs,.elm,.purs,.clj,.edn

# File extensions considered as media files
media_extensions = .jpg,.jpeg,.png,.gif,.bmp,.svg,.mp4,.avi,.mov,.mp3,.wav,.flac,.ogg,.webm,.mkv

[CustomExtensions]
# Optional: Add any custom extensions for auditing
extensions = .foo,.bar,.example
```

· Notes

top_n: Limits how many of the largest or longest files are shown in the summary
max_lines:Limits lines printed per file; files exceeding this will be truncated
max_size:Skips files larger than this size to prevent long processing times
[`FileTypes`]:Classify files by type (code, docs, media) for filtering options
[`CustomExtensions`]:Allows you to define additional extensions you want dat to process

---

## Summary

`dat` is a versatile audit and file content printing tool for developers. It helps you inspect all files, filter by type, summarize top files, generate PDF reports, process single files, and optionally save results to various formats — all in a single, cross-platform utility.

---

## Output Example

```
DEV AUDIT SUMMARY
================================
Total files processed: 120
Total lines: 12,345
Total size: 24.8 MB
Code files: 45, Docs: 35, Media: 30, Other: 10

Top 5 files by lines:
  2456 lines | ./src/main.py
  1789 lines | ./lib/utils.py
  ...

Top 5 files by size:
     3.5 MB | ./assets/video.mp4
     1.2 MB | ./docs/manual.pdf
  ...
```

---

## Bootstrap / First Run

On first run, `dat` will attempt to install itself as a command for easy access:

· Linux/macOS: Auto-install to `~/.local/bin/dat`
· Windows: Auto-install to `%LOCALAPPDATA%\Programs\Python\Scripts\dat.exe` and optionally add to PATH
· NEW: Native Termux: Auto-install to `/data/data/com.termux/files/usr/bin/dat`
· NEW: Android Linux environments: Auto-install to `~/.local/bin/dat`

Use `--no-bootstrap` to skip this step.

---

## Platform Support

`dat` automatically detects your environment:

· Native Termux: Uses Termux-specific paths
· Android Linux (Andronix/UserLAnd): Uses standard Linux paths
· Windows: Native Windows support with PATH management
· Linux/macOS: Standard Unix paths

---

## Requirements

Python 3.6+
`python-magic(or` `python-magic-bin` on Windows, `reportlab` for PDF output

---

## License

MIT License – See [LICENSE](./LICENSE)

---

## Changelog v2.0.0

· NEW: Single file processing with -s/--single flags
· NEW: PDF report generation support
· NEW: Automatic file extension resolution
· ENHANCED: Robust ignore patterns with -i/-I flags
· ENHANCED: Improved Android/Termux detection
· FIXED: Extension parsing for both .py and py formats
· FIXED: Max file size handling throughout processing chain


