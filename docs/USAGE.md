# Usage Guide

> *"To read a system is to read its soul."*  
> — ~JADIS

The **Dev Audit Tool (`dat`)** lets you explore the full contents of your project — every file, every subdirectory, every extension — with clarity, flexibility, and precision.

Whether you want to audit all code files, generate a documentation summary, or print everything for deep introspection, `dat` gives you full control from the command line.

---

## 🧭 Basic Syntax

```bash
dat [path] [options]

path: Optional. If not provided, dat runs in the current working directory.

options: Control what is shown, how deep the scan goes, and how results are printed.
```


---

# 🗂️ Core Commands

Command	Description
```
dat	Print all files (recursive by default).
dat -a	Include hidden files and folders (dotfiles).
dat -f	Only show current folder, no recursion.
dat -c	Show only code files (e.g., .py, .js, .cpp, etc.).
dat -d	Show only documentation files (e.g., .md, .txt, .rst).
dat -m	Show only media files (e.g., .jpg, .mp4, .svg).
dat -e py,html,js	Show only specific file extensions.
dat -o output.txt	Save all output to a file.
```


---

### 🎛️ Advanced Options

Flag	Description
```
--max-lines	Limit how many lines are printed per file.
--max-size	Skip files larger than this size (in bytes).
--top-n	Show top N files by size or line count in summary.
--no-bootstrap	Skip automatic installation/setup.
--version	Show version, environment, and platform info.
```


---

# 🌍 Practical Examples

## 🔍 Audit Everything
```
dat
```
Scans all files and subdirectories from the current folder.


---

## 📜 Documentation-Only Audit
```
dat -d
```
Lists and prints only documentation files (.md, .txt, .rst, etc.).


---

## 💻 Code-Only Audit
```
dat -c
```
Focuses only on programming and configuration files.


---

## 🔒 Current Folder Only
```
dat -f
```
Skips recursion and audits only the current directory level.


---

## 🔦 Include Hidden Files
```
dat -a
```
Also prints dotfiles and hidden directories like .config or .env.


---

## 🧩 Combine Options
```
dat -c -a --max-lines 200 -o code_audit.txt
```
Recursively print all code files, include hidden files, limit output per file, and save to code_audit.txt.


---

## 📈 Show Top 10 Largest Files
```
dat --top-n 10
```
Displays a summary table at the end showing the 10 largest or longest files.


---

## 📊 Example Output
```
DEV AUDIT SUMMARY
===============================
Total files processed: 120
Total lines: 12,345
Total size: 24.8 MB
Code files: 45 | Docs: 35 | Media: 30 | Other: 10

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

## ⚙️ Configuration Overrides

dat automatically loads configuration from ~/.datconfig (if present).
CLI options override configuration file settings.
```
dat -c --max-lines 500 --top-n 5
```

---

## 🧱 Bootstrap and Shim Mode

On first run, dat creates a lightweight shell shim to enable easy execution anywhere:
```
dat
```
If you prefer to skip this:
```
dat --no-bootstrap
```

---

## 🪶 Tips & Tricks

Combine -c (code) and -a (all) to audit entire repos, including hidden build files.

Use -f when testing dat locally to limit scope.

Use -o to create traceable audit logs for CI/CD or repository snapshots.

Pair with grep, awk, or less for focused analysis.



---

## 💡 Philosophy

dat isn’t just for code — it’s a lens for understanding structure.
When you run it, you’re not just listing files — you’re seeing the system breathe.

> “Code isn’t chaos; it’s choreography.
Every file tells a fragment of the dance.” — ~JADIS




---

## 🧩 See Also

Configuration Guide

CLI Reference

Troubleshooting



---

© 2025 ~JADIS | Justadudeinspace

---
