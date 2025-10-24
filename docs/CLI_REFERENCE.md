# Command-Line Reference

## Overview

dat provides a comprehensive set of CLI options for enterprise-grade security auditing, compliance scanning, and reporting.

---

## Basic Usage

```bash
dat [path] [options]

If [path] is omitted, dat operates in the current directory.
```

---

## Core Commands

Scan Target
```
Option Long Form Description
[PATH]  Directory to scan (default: current directory)
-f, --folder PATH  Scan only specific folder
-s, --single-file FILE  Scan only specific file
-a, --all  Include hidden files and directories
```
Scanning Modes
```
Option Long Form Description Default
-s, --safe  Safe mode (skip large/binary files) enabled
--no-safe  Disable safe mode limitations 
-p, --deep  Deep scan (include binary analysis) 
--fast  Fast scan (optimized for speed) 
--audit  Compliance audit mode 
```
File Selection & Filtering
```
Option Long Form Description
-c, --code  Only include code files
-d, --docs  Only include documentation files
-m, --media  Only include media files
-e, --ext EXTENSIONS  Custom comma-separated extensions
-i, --ignore PATTERNS  Exclude files matching patterns
--only PATTERNS  Only scan specific patterns
--ignore-file PATH  Read ignore patterns from file
```
Output Formats
```
Option Long Form Description Format
-o, --output FILE  Write report (auto-detects format) Auto
--report FILE  Alias for --output Auto
--json FILE  Write JSON report JSON
--jsonl FILE  Write JSON Lines report JSONL
--pdf FILE  Write PDF report PDF
--md, --markdown FILE  Write Markdown report Markdown
```
Enterprise Features
```
Option Long Form Description
--from-lrc [PATH]  Enable LRC compliance integration
--sign  Sign artifacts with GPG
--no-sign  Disable artifact signing
--diff BASELINE  Compare against previous scan
--interactive  Enable confirmation prompts
```
Performance & Limits
```
Option Long Form Description Default
--max-lines N  Maximum lines per file in safe mode 1000
--max-size N  Maximum file size in bytes 10MB
--top-n N  Display top N files in summary 5
--parallel-threads N  Number of scanning threads auto
--max-depth N  Maximum directory depth (0=unlimited) 0
--batch-size N  Files per processing batch 1000
```
Information & Debugging
```
Option Long Form Description
-v, --verbose  Enable detailed output
--debug  Enable debug-level logging
--version  Show version and build information
--stats  Show detailed statistics
--profile  Profile scanning performance
--validate-config  Validate configuration without scanning
```
---

## Advanced Options

Security & Compliance

```bash
# Compliance framework scanning
dat . --compliance soc2,gdpr,hipaa

# Security policy enforcement
dat . --fail-on-critical --max-violations 0

# Regulatory compliance
dat . --regulation pci-dss,iso27001
```

CI/CD Integration

```bash
# Non-interactive mode
dat . --no-interactive --json output.json

# Exit codes for automation
dat . --no-critical-violations

# Evidence collection
dat . --bundle-evidence --output-dir ./artifacts
```

Environment Configuration

```bash
# Configuration file
dat . --config /path/to/config.ini

# Environment variables
DAT_CONFIG_DIR=/custom/path dat .

# Temporary overrides
dat . --setting max_size=5242880 --setting max_lines=5000
```

---

## Examples

Basic Scanning

```bash
# Quick security scan
dat .

# Deep security audit  
dat . --deep

# Scan specific folder only
dat -f src --code

# Single file analysis
dat -s config.py --verbose
```

Output Management

```bash
# Multiple report formats
dat . --json audit.json --pdf report.pdf --md summary.md

# Auto-detect format from extension
dat . -o scan.jsonl

# Signed compliance report
dat . --from-lrc --pdf compliance.pdf --sign
```

Enterprise Workflows

```bash
# Full compliance audit
dat . --from-lrc --audit --sign --verbose

# Compare with baseline
dat . --diff previous-scan.json

# CI/CD pipeline integration
dat . --json output.json --no-critical-violations
```

Performance Tuning

```bash
# Large repository optimization
dat . --deep --max-size 50MB --max-lines 5000 --parallel-threads 8

# Memory-constrained environment
dat . --batch-size 500 --max-memory 2048

# Focused scanning
dat . --only "*.py,*.js,*.yaml" --ignore "node_modules,dist,tests"
```

Filtering Examples

```bash
# Exclude common directories
dat . --ignore "node_modules,__pycache__,.git,dist,build"

# Only security-related files
dat . --only "*.py,*.js,*.yaml,*.yml,*.json,*.config"

# Custom file types
dat . -e "go,rs,ts,jsx,tsx" --top-n 20
```

---

## Return Codes
```
Code Meaning Typical Use Case
0 Success Scan completed successfully
1 Error Invalid arguments, file not found, permissions
2 Dependency Missing dependencies, environment issues
3 Violations Policy violations detected (regressions)
4 Configuration Invalid configuration, schema errors
5 Security Security policy violation, critical issues
130 Interrupted User interrupted (Ctrl+C)
255 Fatal Unexpected error, system failure
```
CI/CD Integration Examples

```bash
# Fail build on critical violations
dat . --from-lrc --json audit.json
if [ $? -eq 3 ]; then
    echo "Critical violations detected - failing build"
    exit 1
fi

# Only fail on new regressions
dat . --diff baseline.json --json current.json
exit_code=$?
if [ $exit_code -eq 3 ]; then
    echo "New violations detected"
    exit 1
elif [ $exit_code -eq 0 ]; then
    echo "Scan passed - no regressions"
fi
```

---

## Environment Variables
```
Variable Description Default
DAT_CONFIG_DIR Configuration directory ~/.config/dat
DAT_NO_COLOR Disable colored output false
DAT_DEBUG Enable debug output false
DAT_SIGNING_KEY GPG key ID for signing system default
LRC_CONFIG_PATH LRC configuration file ~/.config/lrc/dat_integration.json
DAT_LOG_LEVEL Logging verbosity info
DAT_MAX_MEMORY Memory limit (MB) unlimited
```
---

## Configuration Precedence

1. CLI Arguments - Highest priority, direct overrides
2. Environment Variables - Runtime environment settings
3. Project Config - ./.datconfig in repository root
4. Global Config - ~/.config/dat/config.ini
5. Default Values - Built-in safe defaults

```bash
# Example showing precedence
dat . --max-size 5242880  # CLI overrides config file
```

---
