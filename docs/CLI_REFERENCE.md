⚙️ docs/CLI_REFERENCE.md

# Command-Line Reference

## Overview
`dat` provides a comprehensive set of CLI options for file auditing, inspection, and reporting.

---

## Basic Usage
```bash
dat [path] [options]

If [path] is omitted, dat operates in the current directory.
```

---
```
Core Options

Option	Long Form	Description

-a	--all	Include hidden files and folders.
-f	--flat	Only process the current folder (no recursion).
-c	--code	Only include code-related file types.
-d	--docs	Only include documentation files.
-m	--media	Only include media files.
-e	--ext	Custom comma-separated extensions.
-o	--output	Write output to specified file.
	--max-lines	Limit number of lines shown per file.
	--max-size	Maximum file size to process (bytes).
	--top-n	Display N largest or longest files.
	--no-bootstrap	Skip auto-install and environment setup.
	--version	Show tool version and environment info.

```

---

## Examples
```
# Print all files recursively
dat -a

# Show only code files
dat -c

# Output audit to file
dat -a -o full_audit.txt

# Limit display to top 10 largest files
dat --top-n 10
```


## Return Codes
```
Code	Meaning

0	Success
1	Error (invalid path, missing file, etc.)
2	Dependency or environment issue
```

---
