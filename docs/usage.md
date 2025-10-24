# DAT Enterprise Usage Guide

The Dev Audit Tool (DAT) provides comprehensive security and compliance scanning through a unified `dat` command. This guide covers both basic usage and enterprise features.

## Quick Start

### Basic Scan
```bash
# Scan current directory with safe defaults
dat .

# Generate JSON report
dat . --report audit.json

# Scan specific repository
dat /path/to/repo --report /output/audit.json
```

### Enterprise Scan with LRC Integration

```bash
# Full enterprise workflow
dat . --from-lrc --report audit.json --output report.pdf --sign --verbose
```

## Core Scanning Modes

### Safe Mode (Default)

· Enabled by default: --safe or -s
· Skips: Files >10MB or >1000 lines
· Excludes: Binary files by default
· Best for: Regular development workflows

```bash
dat . --safe                    # Explicit safe mode (default)
dat . --no-safe                 # Disable safe mode
```

### Deep Scan Mode

· Flag: --deep or -p
· Reads: All files regardless of size or type
· Includes: Binary file analysis
· Best for: CI/CD pipelines, security audits

```bash
# Full deep scan
dat . --deep

# Deep scan but keep size limits
dat . --deep --safe

# Unrestricted deep scan
dat . --deep --no-safe
```

## File Exclusion Patterns

### Exclude files and directories using glob patterns:

```bash
# Single pattern
dat . --ignore "node_modules"

# Multiple patterns
dat . --ignore "*.pyc" --ignore "*.log" --ignore "temp/"

# Complex patterns
dat . --ignore "**/__pycache__" --ignore "dist/*" --ignore "*.min.js"

# Pattern files (enterprise feature)
dat . --ignore-file .daignore
```

### Pattern Examples

· "*.pyc" - All Python cache files
· "node_modules/" - Node.js dependencies directory
· "**/test*" - All files starting with 'test' in any directory
· "*.{log,tmp}" - Files with .log or .tmp extensions

## Comprehensive Reporting

### Report Formats

Format Flag Description Use Case
JSONL --jsonl <path> JSON Lines format CI/CD integration
JSON --report <path> Standard JSON Manual review
PDF --pdf <path> Printable report Compliance audits
Auto -o/--output <path> Format by extension Flexible output

### Report Generation Examples

```bash
# Multiple report formats
dat . --jsonl scan.jsonl --pdf report.pdf

# Auto-detect format from extension
dat . --output scan.json    # Creates JSON
dat . --output scan.jsonl   # Creates JSONL  
dat . --output report.pdf   # Creates PDF

# Default behavior (no output flags)
# Creates dat-report.jsonl in current directory
dat .
```

## Report Content

### All reports include:

· Repository fingerprint (SHA256)
· Scan timestamp and duration
· File statistics and violation summary
· LRC metadata (when using --from-lrc)
· User and environment context

## Advanced Comparison Features

### Diff Against Baseline

```bash
# Compare with previous scan
dat . --report current.json --diff baseline.json

# CI pipeline integration
dat . --diff previous-scan.json --no-critical-violations
```

### Diff Output Examples

```
[WARNING] Differences detected compared to baseline
[REGression] src/config.py: violations increased from 2 to 5
[IMPROVEMENT] src/utils.py: violations decreased from 8 to 1
[NEW] src/auth.py: 3 new violations
```

### Exit Codes for CI Integration

· 0: No differences or improvements
· 3: New violations detected (regressions)
· 1: Critical violations exceed threshold

## Enterprise Integration

### LRC Metadata Integration

```bash
# Auto-detect LRC configuration
dat . --from-lrc

# Custom LRC config path
dat . --from-lrc /etc/enterprise/lrc-config.json

# Full enterprise scan
dat . --from-lrc --sign --report audit.json --output compliance.pdf
```

### Artifact Signing

```bash
# Enable signing (default)
dat . --sign

# Disable signing
dat . --no-sign

# Verify signatures
gpg --verify audit.json.asc audit.json
```

### Interactive Mode

```bash
# Confirm before scanning
dat . --interactive
? Scan repository at /home/user/repo? [y/N]: y

# CI-friendly with defaults
dat . --interactive --no-prompt-once
```

## Performance Tuning

### Resource Limits

```bash
# Custom size limits
dat . --max-size 5242880      # 5MB limit
dat . --max-lines 5000        # 5000 lines per file

# Memory optimization for large repos
dat . --batch-size 1000 --parallel-scans 4
```

### Scan Optimization

```bash
# Fast scan (skip binary analysis)
dat . --fast

# Focus on specific file types
dat . --include "*.py" --include "*.js"

# Exclude generated files
dat . --ignore "dist/" --ignore "build/" --ignore "*.min.*"
```

## Environment Configuration

### Configuration Files

```bash
# Global configuration
~/.config/dat/config.json

# Project-specific configuration
./.dat/config.json
```

### Environment Variables

Variable Purpose Default
LRC_CONFIG_PATH LRC configuration file ~/.config/lrc/dat_integration.json
DAT_CONFIG_DIR DAT configuration directory ~/.config/dat/
DAT_LOG_LEVEL Logging verbosity INFO
DAT_NO_COLOR Disable colored output false
DAT_DEBUG Enable debug output false

### Example Configuration

```bash
# Set custom LRC config
export LRC_CONFIG_PATH=/opt/enterprise/lrc.json

# Enable debug mode
export DAT_DEBUG=1

# Disable colors for CI
export DAT_NO_COLOR=1
```

## Troubleshooting Guide

### Common Issues

#### GPGSigning Failures

```bash
# Check GPG installation
gpg --version

# List available keys
gpg --list-secret-keys

# Configure DAT to use specific key
export DAT_SIGNING_KEY=ABCD1234
```

#### File Detection Issues

```bash
# Install libmagic for better file type detection
sudo apt-get install libmagic1  # Ubuntu/Debian
brew install libmagic           # macOS

# Use fallback mode
dat . --no-magic
```

#### Performance Problems

```bash
# Reduce parallelism for resource-constrained environments
dat . --parallel-scans 2

# Limit memory usage
dat . --max-memory 1024

# Enable progress monitoring
dat . --progress
```

#### Debug Mode

```bash
# Enable verbose debugging
dat . --verbose --debug

# Environment debug mode
DAT_DEBUG=1 dat . --from-lrc

# Profile performance
dat . --profile --report profile.json
```

### Recovery Procedures

#### Reset Configuration

```bash
# Remove corrupted configuration
rm -rf ~/.config/dat/

# Regenerate default config
dat --init-config
```

#### Rotate Encryption Keys

```bash
# Backup existing logs
cp -r ~/.config/dat/ ~/.config/dat.backup/

# Remove key (previous logs become unreadable)
rm ~/.config/dat/auditlog.key

# New key will be generated on next run
dat . --report new-scan.json
```

### CI/CD Integration Examples

#### GitHub Actions

```yaml
- name: Security Audit
  run: |
    dat . --from-lrc --report audit.json --diff baseline.json
    if [ $? -eq 3 ]; then
      echo "New violations detected"
      exit 1
    fi
```

#### GitLab CI

```yaml
security_scan:
  script:
    - dat . --from-lrc --report audit.json --sign
  artifacts:
    paths:
      - audit.json
      - audit.json.asc
```

#### Jenkins Pipeline

```groovy
stage('Security Audit') {
  steps {
    sh 'dat . --from-lrc --report audit.json --no-critical-violations'
    archiveArtifacts 'audit.json, audit.json.asc'
  }
}
```

### Best Practices

#### Regular Scanning

```bash
# Daily development scan
dat . --safe --report scan-$(date +%Y%m%d).jsonl

# Pre-commit hook
dat . --staged --report pre-commit-scan.jsonl

# Release validation
dat . --deep --from-lrc --sign --report release-audit.json
```

## Configuration Management

· Store .daignore files in repositories
· Use environment-specific LRC configurations
· Regular key rotation for signing certificates
· Monitor scan performance and adjust limits
