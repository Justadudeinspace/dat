# Configuration Guide

> *"Order isn't restriction — it's rhythm.  
> Configuration is the tempo that keeps a system in tune."*  
> — ~JADIS

This guide explains how to configure and customize **`dat` (Dev Audit Tool)** for enterprise security scanning, compliance auditing, and automated workflows.

---

## 🧭 Overview

`dat` is built to be **self-configuring by default** — no setup is required to run basic security audits.  
However, for enterprise control, compliance requirements, and persistent security policies, you can create configuration files at multiple levels.

### Configuration Locations
- **Global**: `~/.config/dat/config.ini` (enterprise settings)
- **Project**: `./.datconfig` (repository-specific)
- **Environment**: `DAT_*` variables (CI/CD, containers)
- **LRC**: `~/.config/lrc/dat_integration.json` (compliance)

When present, `dat` reads these files automatically on startup.  
Any command-line option will **override** configuration settings.

---

## 🗂️ Configuration File Formats

### INI Format (Recommended - `config.ini`)
```ini
[Settings]
top_n = 10
max_lines = 1000
max_size = 10485760
default_mode = safe
color = auto
default_format = jsonl
progress_bars = true

[Security]
require_signing = false
audit_logging = true
max_violations = 0
fail_on_critical = false
path_traversal_protection = true
validate_extensions = true

[FileTypes]
doc_extensions = .md, .txt, .rst, .pdf, .doc, .docx, .odt
code_extensions = .py, .js, .java, .cpp, .c, .html, .css, .rb, .php, .go
config_extensions = .json, .yaml, .yml, .toml, .ini, .cfg, .conf
media_extensions = .jpg, .jpeg, .png, .gif, .svg, .mp4, .mp3
binary_extensions = .exe, .dll, .so, .dylib, .bin, .app, .zip, .tar
data_extensions = .csv, .tsv, .xlsx, .xls, .db, .sqlite

[LRC]
enabled = false
config_path = 
auto_apply_schemas = true
require_signed_configs = false
compliance_frameworks = soc2, gdpr, hipaa, pcidss

[Rules]
enable_default_rules = true
custom_rules = 
severity_mappings = 
    critical = .*secret.*, .*password.*, .*api[_-]?key.*, .*token.*
    high = .*todo.*, .*fixme.*, .*hack.*, .*xxx.*
    medium = .*debug.*, .*console\.log.*, .*print.*
    low = .*note.*, .*optimize.*, .*review.*

[Scanning]
parallel_threads = auto
default_encoding = utf-8
detect_binary_files = true
max_depth = 0
follow_symlinks = false
scan_hidden = true
always_ignore = 
    **/.git/**
    **/__pycache__/**
    **/node_modules/**
    **/.venv/**
    **/venv/**
    **/target/**
    **/build/**
    **/dist/**
    **/*.egg-info/**
    **/.DS_Store
    **/Thumbs.db

[Output]
output_dir = ./reports
timestamp_format = %Y%m%d_%H%M%S
include_file_contents = false
max_content_length = 1024
compress_json = false
pdf_theme = light
pdf_executive_summary = true

[Enterprise]
enterprise_mode = false
organization_name = 
department = 
compliance_contact = 
retention_days = 90
auto_upload = false
encryption_key = 

[Debug]
debug = false
log_file = ${HOME}/.cache/dat/dat.log
log_level = info
profile_performance = false
keep_temp_files = false
verbose = false
```

YAML Format (Legacy - .datconfig)

```yaml
# Default scan path
path: ~/projects

# File type filters
include_extensions:
  - py
  - md
  - sh
  - json
  - yaml
  - yml

# Excluded paths
exclude_dirs:
  - node_modules
  - .git
  - __pycache__
  - dist
  - build

# Output settings
output_file: ~/dat-audit.log
max_lines: 250
max_size: 500000  # bytes
top_n: 10

# Security settings
audit_logging: true
require_signing: false

# Flags
recursive: true
include_hidden: false
color_output: true
log_level: info
```

---

## 🧩 Configuration Sections

[Settings] - Core Behavior
```
Key Type Default Description
top_n integer 5 Top files to display in summary
max_lines integer 1000 Maximum lines per file in safe mode
max_size integer 10485760 Maximum file size (10MB) in safe mode
default_mode string safe Default scan mode (safe/deep/aggressive)
color string auto Color output (auto/always/never)
default_format string jsonl Default output format
progress_bars boolean true Show progress indicators
```
[Security] - Security & Compliance
```
Key Type Default Description
require_signing boolean false Require GPG signing for reports
audit_logging boolean true Enable encrypted audit logging
max_violations integer 0 Maximum allowed violations before failing
fail_on_critical boolean false Fail on critical violations
path_traversal_protection boolean true Enable path traversal protection
validate_extensions boolean true Validate file extensions for security
```
[FileTypes] - File Categorization
```
Key Type Description
doc_extensions list Documentation files
code_extensions list Source code files
config_extensions list Configuration files
media_extensions list Media files
binary_extensions list Binary/executable files
data_extensions list Data files
```
[LRC] - Compliance Integration
```
Key Type Default Description
enabled boolean false Enable LRC integration
config_path string  Path to LRC configuration
auto_apply_schemas boolean true Auto-apply LRC schemas
require_signed_configs boolean false Require signed LRC configurations
compliance_frameworks list soc2,gdpr,hipaa,pcidss Default compliance frameworks
```
[Rules] - Custom Rules Engine
```
Key Type Default Description
enable_default_rules boolean true Enable built-in security rules
custom_rules list  Custom rule patterns (regex supported)
severity_mappings dict  Rule severity mappings
```
[Scanning] - Performance & Behavior
```
Key Type Default Description
parallel_threads string/integer auto Number of parallel scanning threads
default_encoding string utf-8 File encoding detection
detect_binary_files boolean true Enable binary file detection
max_depth integer 0 Maximum directory depth (0=unlimited)
follow_symlinks boolean false Follow symbolic links
scan_hidden boolean true Scan hidden files/directories
always_ignore list  File patterns to always ignore
```
[Output] - Report Configuration
```
Key Type Default Description
output_dir string ./reports Default output directory
timestamp_format string %Y%m%d_%H%M%S Timestamp format for reports
include_file_contents boolean false Include file contents in JSON reports
max_content_length integer 1024 Maximum file content length to include
compress_json boolean false Compress JSON outputs
pdf_theme string light PDF report theme (light/dark/corporate)
pdf_executive_summary boolean true Enable executive summary in PDF
```
[Enterprise] - Enterprise Features
```
Key Type Default Description
enterprise_mode boolean false Enable enterprise mode
organization_name string  Organization name for reports
department string  Department/team name
compliance_contact string  Compliance officer contact
retention_days integer 90 Audit retention period (days)
auto_upload boolean false Auto-upload to compliance system
encryption_key string  Encryption key for sensitive data
```
[Debug] - Development & Debugging
```
Key Type Default Description
debug boolean false Enable debug logging
log_file string ${HOME}/.cache/dat/dat.log Log file path
log_level string info Log level (debug/info/warning/error)
profile_performance boolean false Profile scanning performance
keep_temp_files boolean false Keep temporary files
verbose boolean false Verbose output mode
```
---

## 🧠 Environment Variables

You can also configure dat via environment variables, essential for CI/CD, containers, and automation.
```
Variable Description Example
DAT_CONFIG_DIR Configuration directory export DAT_CONFIG_DIR=/opt/dat/config
DAT_NO_COLOR Disable colored output export DAT_NO_COLOR=1
DAT_DEBUG Enable debug output export DAT_DEBUG=1
DAT_SIGNING_KEY GPG key ID for signing export DAT_SIGNING_KEY=ABCD1234
DAT_LOG_LEVEL Logging verbosity export DAT_LOG_LEVEL=debug
DAT_MAX_MEMORY Memory limit (MB) export DAT_MAX_MEMORY=2048
LRC_CONFIG_PATH LRC configuration file export LRC_CONFIG_PATH=/etc/lrc/config.json
DAT_OUTPUT_DIR Output directory export DAT_OUTPUT_DIR=/reports
DAT_MAX_VIOLATIONS Maximum violations export DAT_MAX_VIOLATIONS=10
```
Precedence: Environment variables override config file settings, and both are overridden by CLI flags.

---

## 🔧 Configuration Precedence

```
1. CLI Arguments (Highest Priority)
   dat . --max-lines 500 --deep --sign

2. Environment Variables
   export DAT_MAX_LINES=1000
   export DAT_SIGNING_KEY=KEY_ID

3. Project Config (./.datconfig)
   [Settings]
   max_lines = 2000

4. Global Config (~/.config/dat/config.ini)
   [Settings]
   max_lines = 1000

5. Default Values (Lowest Priority)
   max_lines = 1000
```

---

## 🧱 Local Project Configuration

Each repository can include a local .datconfig file for project-specific settings that don't affect global defaults.

Example Project Configuration

```ini
# .datconfig - Project-specific settings
[Settings]
top_n = 20
max_lines = 5000

[Rules]
custom_rules = 
    project.license_header = Copyright 2024.*Company
    project.api_endpoints = /api/v[0-9]+/

[Scanning]
always_ignore = 
    **/tests/**
    **/fixtures/**
    **/migrations/**
    local_*.py
```

Git Integration

```bash
# Add to .gitignore if contains sensitive paths
echo ".datconfig" >> .gitignore

# Or version control for team settings
git add .datconfig
```

---

## 🏢 Enterprise Configuration Examples

Basic Security Scanning

```ini
[Settings]
default_mode = safe
default_format = jsonl
top_n = 10

[Security]
audit_logging = true
path_traversal_protection = true
validate_extensions = true

[Scanning]
always_ignore = 
    **/.git/**
    **/node_modules/**
    **/__pycache__/**
    **/dist/**
    **/build/**
```

Compliance-Focused

```ini
[Settings]
default_mode = deep
default_format = pdf

[Security]
require_signing = true
audit_logging = true
fail_on_critical = true
max_violations = 0

[LRC]
enabled = true
auto_apply_schemas = true
compliance_frameworks = soc2, gdpr, hipaa

[Enterprise]
enterprise_mode = true
organization_name = Acme Corporation
compliance_contact = security@acme.com
retention_days = 365
```

Development Team

```ini
[Settings]
default_mode = safe
color = always
progress_bars = true

[Rules]
enable_default_rules = true
severity_mappings = 
    critical = .*secret.*, .*password.*, .*api_key.*
    high = .*todo.*, .*fixme.*, .*hack.*
    medium = .*debug.*, .*console\.log.*
    low = .*note.*, .*optimize.*

[Output]
output_dir = ./reports
pdf_theme = light
pdf_executive_summary = true
```

---

## 🧭 Validation and Diagnostics

When you run dat, it performs configuration validation:

```bash
# Check configuration
dat --validate-config

# Show effective configuration
dat --show-config

# Debug configuration loading
DAT_DEBUG=1 dat . --verbose
```

Validation Output

```
✅ Configuration loaded from ~/.config/dat/config.ini
✅ 15 valid settings applied
⚠️  Unrecognized key: 'legacy_setting' (ignored)
✅ Security features: audit_logging, path_protection
✅ LRC integration: disabled
```

If any essential values are missing, dat automatically applies safe defaults and logs warnings.

---

## 🔒 Security Configuration Best Practices

For Production

```ini
[Security]
require_signing = true
audit_logging = true
fail_on_critical = true
max_violations = 0
path_traversal_protection = true
validate_extensions = true

[Enterprise]
enterprise_mode = true
retention_days = 90
auto_upload = false
```

For CI/CD Pipelines

```ini
[Settings]
default_mode = safe
default_format = json
progress_bars = false

[Security]
audit_logging = true
max_violations = 10

[Output]
output_dir = ${CI_PROJECT_DIR}/reports
timestamp_format = %Y%m%d_%H%M%S
```

---

## 💡 Example Workflows

Development Setup

```bash
# 1. Create global configuration
mkdir -p ~/.config/dat
cat > ~/.config/dat/config.ini << 'EOF'
[Settings]
default_mode = safe
color = auto
top_n = 10

[Security]
audit_logging = true
EOF

# 2. Run security scan
dat .

# 3. Create project-specific settings
cat > .datconfig << 'EOF'
[Settings]
max_lines = 5000
top_n = 20

[Scanning]
always_ignore = 
    **/tests/**
    **/fixtures/**
EOF

# 4. Scan with project settings
dat . --verbose
```

Enterprise Deployment

```bash
# 1. Set up enterprise configuration
sudo mkdir -p /etc/dat
sudo cat > /etc/dat/config.ini << 'EOF'
[Settings]
default_mode = deep
default_format = pdf

[Security]
require_signing = true
audit_logging = true
fail_on_critical = true

[Enterprise]
enterprise_mode = true
organization_name = "Acme Corp"
retention_days = 90
EOF

# 2. Configure environment
export DAT_CONFIG_DIR=/etc/dat
export DAT_SIGNING_KEY=ENTERPRISE_KEY_ID

# 3. Run compliance audit
dat . --from-lrc --sign --verbose
```

CI/CD Integration

```yaml
# .gitlab-ci.yml
security_scan:
  variables:
    DAT_CONFIG_DIR: "${CI_PROJECT_DIR}/.dat"
    DAT_NO_COLOR: "1"
    DAT_OUTPUT_DIR: "${CI_PROJECT_DIR}/reports"
  script:
    - dat . --json security-scan.json --no-critical-violations
  artifacts:
    paths:
      - reports/
    reports:
      sast: reports/security-scan.json
```

---

## 🎯 Tips & Best Practices

1. Start Simple: Begin with minimal configuration and add complexity as needed
2. Use Project Configs: Keep global config lightweight, use project configs for overrides
3. Environment Variables: Use for CI/CD, containers, and sensitive data
4. Security First: Enable audit logging and path protection in production
5. Version Control: Consider adding project configs to version control for team consistency
6. Regular Review: Periodically review and update security rules and patterns
7. Backup Configs: Backup global configuration when making significant changes

---

## Philosophy

Configuration isn't just setup — it's intent, formalized.
Every key is a choice, every rule a rhythm in the greater composition of your system.

"When we configure, we are not limiting — we are aligning."
— ~JADIS

---

## 🔗 See Also

· Usage Guide - Practical scanning examples
· CLI Reference - Complete command reference
· Enterprise Features - Advanced configuration options
· Troubleshooting - Configuration debugging

---

© 2025 ~JADIS | Justadudeinspace

---
