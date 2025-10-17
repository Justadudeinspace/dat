# 🌀 CHANGELOG  
> *"Every revision is a ripple — a trace of thought made tangible."*  
> — ~JADIS

All notable changes to this project will be documented in this file.  
This format follows the conventions of [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [Unreleased]
### 🔮 Planned
- Add interactive TUI mode (`dat --tui`) for live file previews.
- Support `.env` file parsing for configuration.
- Extend syntax highlighting for `.yaml`, `.toml`, `.json`.
- Add `--json` and `--csv` output export modes.
- Integrate with `watchdog` for live project monitoring (`dat --watch`).
- Include optional GPT/Gemini “summary” mode to describe codebases in natural language.

---

## [1.0.0] — 2025-10-17  
### 🌟 Initial Release — “Big Picture”

This marks the **first full release** of `dat` — the **Dev Audit Tool** —  
a system-wide visualizer and analyzer designed for transparency, insight, and creative clarity.

#### Added
- Core CLI (`dat`) with recursive directory scanning.
- File type filters:
  - `-a` : include all (visible + hidden)
  - `-v` : visible files only
  - `-d` : documentation only
  - `-c` : code files only
  - `-e EXT` : specific extension filter
  - `-f` : standing directory only
- File summary and global statistics:
  - Per-file line and byte counts.
  - Aggregated totals at end of run.
  - Top N largest/longest files displayed in summary table.
- Config system:
  - Global config (`~/.datconfig`)
  - Local project config (`.datconfig`)
  - Full YAML/INI support.
- Environment variable overrides (`DAT_PATH`, `DAT_MAX_LINES`, etc.)
- Optional colored terminal output with auto-detection.
- Output to file (`-o` or `--output`).
- `bootstrap.sh` for automated setup.
- `sample_output.txt` template for quick verification.
- Test suite:
  - `test_core.py` for scanning logic.
  - `test_cli.py` for argument parsing and integration flow.
- Documentation suite:
  - `README.md`
  - `USAGE.md`
  - `CONFIG.md`
  - `CHANGELOG.md`
  - `/docs` directory structure pre-built.

#### Fixed
- Stabilized path resolution across OSes.
- Correctly handles Unicode and long filenames.
- Prevents recursion loops from symlinks.
- Graceful exit when permission errors occur.

#### Known Issues
- Scanning extremely large repos (>10k files) may slow down summary rendering.
- No current progress bar for long audits.
- Windows path coloring may behave inconsistently under `cmd.exe`.

---

## [0.9.0] — 2025-10-14  
### 🧩 Protoform Build

Early experiment showcasing the recursive file scanning and auto-printing logic.  
Served as the proof of concept that inspired full CLI evolution.

#### Added
- Recursive file walker.
- Basic `cat -a` style full-content print.
- Minimal CLI prototype (`cat.py` → `dat`).
- Preliminary color and indentation logic.

#### Removed
- Experimental debug flags (`--x` and `--xx`).
- Old stdout printer replaced with rich-style output manager.

---

## [0.1.0] — 2025-10-10  
### 🌱 The Seed

The first prototype idea:  
*"What if `cat` could see everything?"*  
This commit held the earliest glimmer of what became the **Big Picture Audit Tool**.

---

## 🧭 Versioning

This project adheres to **Semantic Versioning** (SemVer):  
`MAJOR.MINOR.PATCH` — meaning:

- **MAJOR** for incompatible or architectural changes,  
- **MINOR** for backward-compatible feature additions,  
- **PATCH** for bug fixes and refinements.

---

## 🕊️ Legacy Note

> *"A changelog is not just record — it’s remembrance.  
>  Each entry, a small rebellion against forgetting."*  
>  — ~JADIS

---

© 2025 ~JADIS | Justadudeinspace  
All Rights Reserved under MIT License.
