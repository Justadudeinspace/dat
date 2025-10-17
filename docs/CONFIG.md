# Configuration Guide

> *"Order isn’t restriction — it’s rhythm.  
> Configuration is the tempo that keeps a system in tune."*  
> — ~JADIS

This guide explains how to configure and customize **`dat` (Dev Audit Tool)** for your local environment, automation pipelines, and personal workflow.

---

## 🧭 Overview

`dat` is built to be **self-configuring by default** — no setup is required to run basic audits.  
However, for advanced control and persistent preferences, you can create a configuration file at:
```
~/.datconfig
```
When present, `dat` reads this file automatically on startup.  
Any command-line option will **override** a configuration setting.

---

## 🗂️ Configuration File Format

The configuration file supports both **YAML** and **INI-style key=value** syntax.

### Example (`~/.datconfig`)

```yaml
# Default scan path
path: ~/projects

# File type filters
include_extensions:
  - py
  - md
  - sh
  - json

# Excluded paths
exclude_dirs:
  - node_modules
  - .git
  - __pycache__

# Output settings
output_file: ~/dat-audit.log
max_lines: 250
max_size: 500000  # bytes
top_n: 10

# Flags
recursive: true
include_hidden: false
color_output: true
```

---

## 🧩 Supported Keys

Key	Type	Description
```
path	string	Starting directory to scan. Defaults to current working directory.
include_extensions	list	Limit audit to specific extensions (e.g., ['py', 'md']).
exclude_dirs	list	Skip directories or files matching names in this list.
output_file	string	File path to save results.
max_lines	integer	Limit how many lines of each file are printed.
max_size	integer	Skip files larger than this number of bytes.
top_n	integer	Show top N files by line count or size.
recursive	boolean	Whether to scan subdirectories (default: true).
include_hidden	boolean	Include hidden files and folders.
color_output	boolean	Use ANSI color in terminal output.
log_level	string	Control verbosity (info, warn, debug, error).
```


---

## 🧠 Environment Variables

You can also configure dat via environment variables, useful for CI/CD or containerized runs.

Variable	Description	Example
```
DAT_PATH	Default working directory	export DAT_PATH=~/projects
DAT_OUTPUT	Output file path	export DAT_OUTPUT=~/audit.log
DAT_EXCLUDE	Comma-separated list of directories	export DAT_EXCLUDE=node_modules,.git
DAT_MAX_LINES	Line limit per file	export DAT_MAX_LINES=200
DAT_TOP_N	Show top N largest files	export DAT_TOP_N=5


Environment variables override config file settings,
and both are overridden by CLI flags.
```

---

## 🔧 Configuration Precedence
```
1. CLI Arguments
e.g. dat -c --max-lines 100


2. Environment Variables
e.g. export DAT_MAX_LINES=300


3. User Config File (~/.datconfig)


4. Defaults (built-in settings)
```



---

## 🧱 Local Project Config

Each project can include a local .datconfig file in its root directory.
When present, dat merges it with the global configuration file.

Example .datconfig inside a repo:
```
exclude_dirs:
  - tests
  - logs
top_n: 20
```
This allows per-project customization without affecting your global defaults.


---

## 🧭 Validation and Warnings

When you run dat, it prints a short validation report if a config file is malformed or a key is unrecognized:

⚠️ Warning: Unrecognized key "depth_limit" in ~/.datconfig
✅ Loaded 10 valid configuration options

If any essential values are missing, dat automatically applies safe defaults.


---

##  Tips & Best Practices

Keep your global config lightweight, and use project configs for overrides.

Add .datconfig to .gitignore if it contains local paths.

For CI pipelines, define configuration via environment variables for portability.

Combine with dat -o to version-track audits automatically.



---

## 💡 Example Workflow
```
# 1. Create or edit your config file
nano ~/.datconfig

# 2. Run a normal audit
dat

# 3. Override config temporarily
dat -c --max-lines 300

# 4. Save the output to a log
dat -o ~/logs/project_audit.txt
```

---

##  Philosophy

Configuration isn’t just setup — it’s intent, formalized.
Every key is a choice, every rule a rhythm in the greater composition of your system.

> "When we configure, we are not limiting — we are aligning."
— ~JADIS




---

## 🔗 See Also

Usage Guide

CLI Reference

Troubleshooting



---

© 2025 ~JADIS | Justadudeinspace

---
