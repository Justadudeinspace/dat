```markdown
### 🧭 `docs/CONFIGURATION.md`

# Configuration

`dat` supports multiple configuration layers for enterprise-grade security scanning and compliance auditing.

## Configuration Locations

### Primary Configuration Files
- **Global**: `~/.config/dat/config.ini` (recommended)
- **Legacy**: `~/.datconfig` (YAML/INI format)
- **Project**: `./.datconfig` (repository-specific)
- **LRC**: `~/.config/lrc/dat_integration.json` (compliance)

### Environment Configuration
- **Environment Variables**: `DAT_*` prefixed variables
- **CI/CD Systems**: Pipeline-specific settings
- **Container Environments**: Runtime configuration

## Example Configuration

### Complete Enterprise Configuration (`config.ini`)
```ini
[Settings]
top_n = 10
max_lines = 1000
max_size = 10485760  # 10 MB
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
doc_extensions = .md,.txt,.rst,.pdf,.docx,.odt
code_extensions = .py,.js,.cpp,.c,.sh,.rs,.java,.go,.ts,.html,.css,.rb,.php
config_extensions = .json,.yaml,.yml,.toml,.ini,.cfg,.conf,.xml
media_extensions = .jpg,.jpeg,.png,.gif,.bmp,.svg,.mp3,.mp4,.avi,.mov
binary_extensions = .exe,.dll,.so,.dylib,.bin,.app,.zip,.tar,.gz
data_extensions = .csv,.tsv,.xlsx,.xls,.db,.sqlite,.parquet

[LRC]
enabled = false
config_path = 
auto_apply_schemas = true
require_signed_configs = false
compliance_frameworks = soc2,gdpr,hipaa,pcidss

[Rules]
enable_default_rules = true
custom_rules = 
    # Example: secret_key=.*
    # Example: password\s*=\s*["'].*["']
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

### Legacy YAML Configuration (~/.datconfig)

```yaml
# Default scan path
path: ~/projects

# File type filters
include_extensions:
  - py
  - js
  - md
  - txt
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
  - .venv

# Output settings
output_file: ~/dat-audit.log
max_lines: 1000
max_size: 10485760
top_n: 10

# Security settings
audit_logging: true
require_signing: false

# Scanning behavior
recursive: true
include_hidden: false
color_output: true
log_level: info
```

### Project-Specific Configuration (./.datconfig)

```ini
[Settings]
top_n = 20
max_lines = 5000

[Rules]
custom_rules = 
    project.license = Copyright.*2024
    project.endpoints = /api/v[0-9]+/

[Scanning]
always_ignore = 
    **/tests/**
    **/fixtures/**
    **/migrations/**
    **/docs/_build/**
    local_*.py
    temp_*.json
```

## Configuration Precedence

### Settings are applied in this order (later overrides earlier):

1. CLI Arguments (highest priority)
   ```bash
   dat . --max-lines 500 --deep --sign
   ```
2. Environment Variables
   ```bash
   export DAT_MAX_LINES=2000
   export DAT_SIGNING_KEY=KEY_ID
   ```
3. Project Configuration (./.datconfig)
4. Global Configuration (~/.config/dat/config.ini)
5. Legacy Configuration (~/.datconfig)
6. Default Values (lowest priority)

### Environment Variables
```
Variable Description Default
DAT_CONFIG_DIR Configuration directory ~/.config/dat
DAT_NO_COLOR Disable colored output false
DAT_DEBUG Enable debug output false
DAT_SIGNING_KEY GPG key for signing system default
DAT_LOG_LEVEL Logging verbosity info
DAT_MAX_MEMORY Memory limit (MB) unlimited
LRC_CONFIG_PATH LRC config file ~/.config/lrc/dat_integration.json
DAT_OUTPUT_DIR Output directory ./reports
``
### Configuration Validation

dat validates configuration on startup and provides feedback:

```bash
# Validate configuration without scanning
dat --validate-config

# Show effective configuration
dat --show-config

# Debug configuration loading
DAT_DEBUG=1 dat . --verbose
```

### Validation Output Example

```
✅ Configuration loaded from ~/.config/dat/config.ini
✅ 28 valid settings applied
⚠️  Unrecognized key: 'legacy_timeout' (ignored)
✅ Security features: audit_logging, path_traversal_protection
✅ LRC integration: disabled (not configured)
✅ File type detection: 5 categories, 127 extensions
```

## Common Configuration Patterns

### Development Team

```ini
[Settings]
top_n = 10
max_lines = 1000
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
```

### Security-Focused

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
compliance_frameworks = soc2,gdpr,hipaa

[Enterprise]
enterprise_mode = true
organization_name = "Security Team"
retention_days = 90
```

### CI/CD Pipeline

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

## Notes

· Missing Values: Revert to internal safe defaults
· Runtime Overrides: CLI flags always override configuration
· Human-Editable: All configuration files are designed for manual editing
· Optional: No configuration required for basic operation
· Backward Compatibility: Legacy .datconfig format supported but deprecated
· Validation: Invalid keys are ignored with warnings
· Security: Sensitive values can use environment variables
