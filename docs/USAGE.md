# Usage Guide

> *"To read a system is to read its soul."*  
> — ~JADIS

The **Dev Audit Tool (`dat`)** provides enterprise-grade security scanning, compliance auditing, and comprehensive code analysis. Whether you're conducting security reviews, compliance audits, or code quality assessments, `dat` delivers precision, flexibility, and enterprise-ready features.

---

## 🧭 Basic Syntax

```bash
dat [path] [options]

path: Optional. If not provided, dat runs in the current working directory.

options: Control scanning behavior, output formats, security policies, and compliance requirements.
```

---

## 🏢 Enterprise Scanning Modes

### 🔒 Safe Mode (Default)

```bash
# Security-focused scanning with safe defaults
dat . --safe

# Skip large files and binaries (recommended for development)
dat . --safe --max-size 10MB --max-lines 1000
```

### 🔍 Deep Scan

```bash
# Comprehensive analysis including binary files
dat . --deep

# No size or line limits
dat . --deep --no-safe
```

### ⚡ Fast Scan

```bash
# Optimized for speed in large repositories
dat . --fast

# Quick security assessment
dat . --fast --json quick-scan.json
```

### 🏛️ Compliance Audit

```bash
# Enterprise compliance scanning
dat . --audit

# Specific compliance frameworks
dat . --compliance soc2,gdpr,hipaa
```

---

## 🎯 File Selection & Filtering

### Core File Type Filters

```bash
# Code files only (Python, JavaScript, Java, etc.)
dat . --code

# Documentation files (Markdown, PDF, text)
dat . --docs

# Media files (images, videos, audio)
dat . --media

# Configuration files (JSON, YAML, INI)
dat . --config

# Custom file extensions
dat . --ext "py,js,ts,go,rs"
```

### Advanced Filtering

```bash
# Include hidden files and directories
dat . --all

# Scan specific folder only
dat . --folder src

# Scan single file
dat . --single-file config.py

# Multiple file selection
dat . --folder src --single-file README.md
```

### Exclusion Patterns

```bash
# Exclude common directories
dat . --ignore "node_modules,__pycache__,.git,dist,build"

# Multiple ignore patterns
dat . --ignore "*.log" --ignore "temp/" --ignore "**/test_*"

# Ignore file with patterns
dat . --ignore-file .gitignore
```

---

## 📊 Output & Reporting

### Multiple Format Support

```bash
# JSON for CI/CD integration
dat . --json security-scan.json

# JSON Lines for streaming
dat . --jsonl stream.jsonl

# PDF for compliance documentation
dat . --pdf compliance-report.pdf

# Markdown for pull requests
dat . --markdown SECURITY_SCAN.md

# Auto-detect format from extension
dat . --output report.json  # Creates JSON
dat . --output report.pdf   # Creates PDF
```

### Enterprise Reporting

```bash
# Comprehensive compliance evidence
dat . --from-lrc --pdf evidence.pdf --json audit.json --sign

# Executive summary for management
dat . --pdf executive-report.pdf --pdf-executive-summary

# Multiple outputs simultaneously
dat . --json detailed.json --pdf summary.pdf --md overview.md
```

### Signed Artifacts

```bash
# GPG signed reports
dat . --sign --report audit.json

# Verify signatures
gpg --verify audit.json.asc audit.json

# Disable signing
dat . --no-sign --report scan.json
```

---

## 🔒 Security & Compliance Features

### LRC Integration

```bash
# Enable compliance scanning
dat . --from-lrc

# Custom LRC configuration
dat . --from-lrc /etc/enterprise/lrc-config.json

# Compliance framework validation
dat . --from-lrc --compliance soc2,gdpr
```

### Policy Enforcement

```bash
# Fail on critical violations
dat . --fail-on-critical

# Set violation thresholds
dat . --max-violations 10

# Exit codes for CI/CD
dat . --no-critical-violations
```

### Audit Logging

```bash
# Encrypted audit trail
dat . --audit-logging

# Custom audit location
export DAT_CONFIG_DIR=/var/log/security
dat . --audit-logging
```

---

## ⚡ Performance Optimization

### Resource Management

```bash
# Limit memory usage
dat . --max-memory 1024  # 1GB

# Control parallel processing
dat . --parallel-threads 4

# Batch processing for large repos
dat . --batch-size 1000
```

### Scan Optimization

```bash
# Limit directory depth
dat . --max-depth 3

# Skip binary analysis
dat . --no-binary-detection

# Fast file type detection
dat . --fast-detection
```

### Large Repository Strategies

```bash
# Focus on critical areas
dat . --folder src --code --config

# Exclude generated files
dat . --ignore "**/node_modules/**,**/dist/**,**/build/**"

# Incremental scanning
dat . --since "24 hours ago"
```

---

## 🌍 Practical Examples

### Daily Development Workflow

```bash
# Quick security check
dat . --safe --json daily-scan-$(date +%Y%m%d).json

# Code quality assessment
dat . --code --markdown code-review.md

# Documentation audit
dat . --docs --pdf documentation-report.pdf
```

### CI/CD Pipeline Integration

```bash
# Security gate in pipeline
dat . --safe --json security-scan.json --no-critical-violations

# Compliance validation
dat . --from-lrc --compliance soc2 --json compliance-check.json

# Evidence collection
dat . --from-lrc --bundle-evidence --output-dir ./artifacts
```

### Enterprise Compliance Audits

```bash
# Full compliance assessment
dat . --from-lrc --audit --sign --verbose

# Framework-specific scanning
dat . --compliance soc2 --pdf soc2-report.pdf

# Evidence package generation
dat . --from-lrc --evidence-package ./compliance-evidence
```

### Pre-commit & Pre-push Hooks

```bash
#!/bin/bash
# Pre-commit hook
dat . --staged --json pre-commit-scan.json
if [ $? -eq 3 ]; then
    echo "Security violations detected - commit blocked"
    exit 1
fi
```

---

## 📈 Advanced Usage Examples

### Security Baseline Comparison

```bash
# Create baseline
dat . --deep --json baseline.json

# Later comparison
dat . --diff baseline.json --json current-scan.json

# Track improvements/regressions
dat . --diff previous-scan.json --verbose
```

### Multi-Project Scanning

```bash
#!/bin/bash
# Scan multiple repositories
for repo in /projects/*; do
    if [ -d "$repo" ]; then
        echo "Scanning $repo"
        dat "$repo" --json "/reports/$(basename $repo).json"
    fi
done
```

### Real-time Monitoring

```bash
# Watch mode for development
while true; do
    dat . --fast --json latest-scan.json
    sleep 300  # 5 minutes
done
```

### Integration with Security Tools

```bash
# Export to security dashboard
dat . --json | curl -X POST -H "Content-Type: application/json" -d @- $DASHBOARD_URL

# SARIF format for GitHub
dat . --sarif security-results.sarif

# JUnit for test reporting
dat . --junit security-tests.xml
```

---

## 🔧 Configuration & Environment

### Configuration Management

```bash
# Show effective configuration
dat --show-config

# Validate configuration
dat --validate-config

# Environment-specific settings
export DAT_CONFIG_DIR=/etc/dat
export DAT_SIGNING_KEY=ENTERPRISE_KEY
```

### Environment Variables

```bash
# Configuration overrides
export DAT_MAX_MEMORY=2048
export DAT_NO_COLOR=1
export DAT_LOG_LEVEL=debug

# Compliance settings
export LRC_CONFIG_PATH=/etc/lrc/dat-config.json
export DAT_COMPLIANCE_FRAMEWORKS="soc2,gdpr,hipaa"
```

---

## 🎛️ Advanced Options Reference

### Scanning Behavior
```
Option Description Default
--safe Safe mode (skip large/binary files) enabled
--deep Deep scan (no limits) disabled
--fast Optimized for speed disabled
--audit Compliance audit mode disabled
--max-depth Maximum directory depth 0 (unlimited)
--follow-symlinks Follow symbolic links false
```
### Output Control
```
Option Description Format
--json JSON report JSON
--jsonl JSON Lines stream JSONL
--pdf PDF document PDF
--markdown Markdown summary Markdown
--output Auto-detect format Auto
--sign GPG sign artifacts ASCII armor
```
### Security Features
```
Option Description Default
--from-lrc LRC compliance integration disabled
--compliance Specific frameworks all
--fail-on-critical Fail on critical violations false
--max-violations Maximum allowed violations 0 (unlimited)
--audit-logging Encrypted audit trail true
```
### Performance Tuning
```
Option Description Default
--max-memory Memory limit (MB) unlimited
--parallel-threads Parallel processing auto
--batch-size Files per batch 1000
--max-size Maximum file size 10MB
--max-lines Maximum lines per file 1000
```
---

## 📊 Example Output

### Comprehensive Security Report

```
DAT ENTERPRISE SECURITY SCAN
============================
Scan Date: 2024-01-15 14:30:22 UTC
Repository: production-service (v2.1.0)
Scanner: DAT v3.0.0-alpha.1

SUMMARY
-------
Files Scanned: 1,245
Total Violations: 23
Critical: 0 ✅ | High: 3 ⚠️ | Medium: 8 ℹ️ | Low: 12 ℹ️
Compliance: SOC2 ✅ | GDPR ✅ | HIPAA ✅
Scan Duration: 45.2 seconds

CRITICAL FINDINGS
-----------------
🚨 No critical violations detected

HIGH SEVERITY FINDINGS
----------------------
🔴 Hardcoded API Key (src/config.py:42)
🔴 Database Password in Code (src/auth.py:15)
🔴 PII Exposure Risk (src/users.py:89)

COMPLIANCE STATUS
-----------------
SOC2: 15/15 controls passed
GDPR: 8/8 articles compliant
HIPAA: 12/12 requirements met

RECOMMENDATIONS
---------------
1. Move secrets to environment variables
2. Implement data encryption at rest
3. Review access control policies
4. Schedule regular security scans
```

---

## 🛠️ Troubleshooting Common Issues

### Performance Problems

```bash
# Reduce resource usage
dat . --fast --max-memory 512 --batch-size 500

# Limit scan scope
dat . --folder src --code --max-depth 2

# Check system resources
free -h && nproc && df -h .
```

### Configuration Issues

```bash
# Validate configuration
dat --validate-config

# Reset to defaults
rm ~/.config/dat/config.ini

# Debug mode
DAT_DEBUG=1 dat . --verbose
```

### Permission Problems

```bash
# Fix script permissions
chmod +x dat

# Use virtual environment
python3 -m venv venv && source venv/bin/activate

# Check file access
ls -la dat && file dat
```

---

# 💡 Philosophy & Best Practices

## Security-First Approach

"Security isn't a feature—it's the foundation. Every scan, every report, every configuration should reinforce the integrity of the system." — ~JADIS

### Best Practices

1. Start Safe: Begin with --safe mode and gradually increase scope
2. Regular Scanning: Integrate into CI/CD for continuous security
3. Evidence Collection: Use --bundle-evidence for compliance audits
4. Sign Artifacts: Always sign reports in production environments
5. Monitor Trends: Use --diff to track security improvements

### Integration Strategy

· Development: Quick scans in pre-commit hooks
· CI/CD: Security gates with --no-critical-violations
· Compliance: Scheduled audits with LRC integration
· Monitoring: Real-time scanning for critical systems

---

## 🔗 See Also

· Configuration Guide - Detailed configuration options
· CLI Reference - Complete command reference
· Enterprise Features - Advanced enterprise capabilities
· Troubleshooting - Problem-solving guide

---

© 2025 ~JADIS | Justadudeinspace

---

DAT transforms security scanning from a checklist activity into a comprehensive security intelligence practice, providing actionable insights and compliance evidence across the entire development lifecycle.
