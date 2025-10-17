# Dev Audit Tool (`dat`) - v1.0.0

> - Author: ~JADIS | Justadudeinspace
> - Updated by: GPT-5, Deepseek AI, & Gemini 2.0 Flash

A comprehensive `developer audit tool` that prints the contents of files in a directory and its subdirectories, with optional filters for code, documentation, or media files. It also supports custom file extensions, line limits, output to files, and detailed summaries.


---

## Features

- Prints contents of all files in a directory and subdirectories

- Filter by file type: code, docs, media, or custom extensions

- Limit the number of lines displayed per file

- Skip large files to save time

- Include hidden files (dotfiles)

- Optionally print current folder only (no recursion)

- Output results to a file

- Display top files by size or line count

- Works cross-platform: Linux, macOS, Windows, Android/Termux

- Supports automatic bootstrap installation

---

## Installation

1. Clone Repo
```
git clone https://github.com/Justadudeinspace/dat.git
cd dat
```

2: Core Python Dependencies
```
pip install -r requirements.txt
```

3: Platform-Specific System Libraries

- Linux (Debian/Ubuntu)
```
sudo apt update && sudo apt install -y libmagic1 libmagic-dev
```
- macOS
```
brew install libmagic
```
- Windows
````
pip install python-magic-bin
```
- Termux / Android
```
pkg install libmagic
pip install -r requirements.txt
```

4. Optional Enhancements
```python
pip install colorama Pillow PyPDF2
```
- Improves colored output (especially on Windows).

- Adds enhanced media/document processing.

5. Run Bootstrap Installer First-Run
```
chmod +x dat
python dat
```

On Windows, you may need to restart your terminal to apply PATH changes.

> Optional: Skip bootstrap with `--no-bootstrap`.

---

## Usage

Print the contents of files in a directory, recursively by default:
```python
# Print all files in current directory and subdirectories
dat
```

---

## Filter by File Type
```python
# Only code files
dat -c

# Only documentation files (markdown, txt, pdf, etc.)
dat -d

# Only media files (images, audio, video)
dat -m

# Custom extensions
dat -e py,js,html
```

---

## Folder Options
```python
# Only current folder, no recursion
dat -f

# Include hidden files
dat -a
```

---

## Output Options
```python
# Output to a file
dat -o audit.txt

# Combine with filters
dat -c -o code_report.txt
```

---

## Advanced Options
```python
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
```python
# Print all code files in project recursively, limit lines to 500, include hidden files, output to file
dat /path/to/project -c -a --max-lines 500 -o code_report.txt

# Print all files with specific extensions in current folder only
dat -f -e py,txt,md

# Print media files under a directory without recursion
dat /path/to/media -m -f
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

- Notes

`top_n`: Limits how many of the largest or longest files are shown in the summary

`max_lines`: Limits lines printed per file; files exceeding this will be truncated

max_size: Skips files larger than this size to prevent long processing times

[FileTypes]: Classify files by type (`code`, `docs`, `media`) for filtering options

[CustomExtensions]: Allows you to define additional extensions you want `dat` to process

---

## Summary

`dat` is a versatile audit and file content printing tool for developers.
It helps you inspect all files, filter by type, summarize top files, and optionally save results to a file — all in a single, cross-platform utility.


---

## Output Example
```
DEV AUDIT SUMMARY
===============================
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

- Linux/macOS/Termux: Auto-install to `~/.local/bin/dat`.

- Windows: Auto-install to `%LOCALAPPDATA%\Programs\Python\Scripts\dat.exe` and optionally add to PATH.


> Use `--no-bootstrap` to skip this step.



---

## Requirements

Python `3.9+`

`python-magic` (or `python-magic-bin` on Windows)

Optional: `colorama`, `Pillow`, `PyPDF2`



---

## License

MIT License – See LICENSE


---
