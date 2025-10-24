# Output Formats

DAT produces multiple enterprise-grade report formats, each optimized for different use cases while maintaining consistent metadata, scan statistics, and policy findings. This ensures seamless transitions between formats without pipeline modifications.

## JSON (`--report audit.json`)

### Features
- **UTF-8 encoded** with newline termination for stream processing
- **Deterministic structure** with sorted keys for reliable diffing
- **Machine-readable** format optimized for CI/CD integration
- **Complete metadata** including scan context and environment details
- **Digital fingerprints** for integrity verification

### Structure
```json
{
  "metadata": {
    "timestamp": "2024-01-15T10:35:22Z",
    "dat_version": "3.0.0-alpha.1",
    "scanner": "DAT Enterprise",
    "user": "security-engineer",
    "repo": "production-service",
    "fingerprint": "sha256:abc123...",
    "environment": {
      "platform": "linux",
      "python_version": "3.11.0"
    }
  },
  "summary": {
    "scanned_files": 245,
    "total_violations": 12,
    "critical_violations": 0,
    "high_violations": 3,
    "medium_violations": 5,
    "low_violations": 4,
    "compliance_status": "compliant",
    "scan_duration_seconds": 45.2
  },
  "scan": {
    "files": [
      {
        "path": "src/main.py",
        "size": 2048,
        "lines": 88,
        "binary": false,
        "checksum": "sha256:def456...",
        "violations": [
          {
            "rule_id": "security.no-secrets",
            "severity": "high",
            "message": "Potential API key detected",
            "line": 42,
            "context": "API_KEY = 'test_key'"
          }
        ]
      }
    ],
    "skipped": [
      {
        "path": "dist/app.bin",
        "reason": "binary_file",
        "size": 5242880
      }
    ]
  },
  "findings": [
    {
      "rule_id": "security.no-secrets",
      "severity": "high",
      "count": 3,
      "files": ["src/config.py", "src/auth.py"]
    }
  ],
  "compliance": {
    "frameworks": ["soc2", "gdpr"],
    "status": {
      "soc2": "compliant",
      "gdpr": "compliant"
    },
    "evidence": {
      "soc2_controls": 15,
      "gdpr_articles": 8
    }
  }
}
```

### Usage Examples

```bash
# Basic JSON output
dat . --json audit.json

# CI/CD integration with exit codes
dat . --json security-scan.json --no-critical-violations

# Compliance-focused JSON
dat . --from-lrc --json compliance-audit.json

# Integration with security tools
dat . --json output.json --format detailed
```

## JSONL (--jsonl audit.jsonl)

### Features

· JSON Lines format for streaming processing
· Real-time output during long scans
· Memory-efficient for large repositories
· Compatible with log processing systems
· Resumable processing for interrupted scans

### Structure

```jsonl
{"type": "metadata", "timestamp": "2024-01-15T10:35:22Z", "dat_version": "3.0.0-alpha.1"}
{"type": "file_scanned", "path": "src/main.py", "size": 2048, "violations": 0}
{"type": "violation", "rule_id": "security.no-secrets", "file": "src/config.py", "line": 42, "severity": "high"}
{"type": "summary", "scanned_files": 245, "total_violations": 12}
```

### Usage Examples

```bash
# JSON Lines for streaming
dat . --jsonl stream.jsonl

# Real-time monitoring
dat . --jsonl - | while read line; do
  echo "Processing: $line"
done

# Integration with Kafka/Logstash
dat . --jsonl | kafka-console-producer --topic security-scans
```

## PDF (--output audit.pdf)

### Features

· Professional layout with corporate branding support
· Multiple themes: light, dark, corporate
· Executive summary for management reviews
· Detailed findings with severity color coding
· Print-optimized for compliance documentation
· Font fallbacks: DejaVu Sans Mono → Courier New

### Report Sections

1. Executive Summary - High-level overview for management
2. Scan Overview - Technical details and environment
3. Findings Summary - Violations by severity and category
4. Detailed Findings - File-by-file analysis
5. Compliance Status - Framework-specific compliance
6. Recommendations - Actionable remediation steps

### Usage Examples

```bash
# Basic PDF report
dat . --pdf security-report.pdf

# Corporate-themed report
dat . --pdf compliance-report.pdf --pdf-theme corporate

# Executive summary only
dat . --pdf executive-summary.pdf --pdf-executive-summary

# Signed compliance evidence
dat . --from-lrc --pdf evidence.pdf --sign
```

## Markdown (--markdown report.md)

### Features

· GitHub/GitLab optimized rendering
· Pull request friendly formatting
· Human-readable with clear section hierarchy
· Code block syntax highlighting support
· Table-based summaries for quick review
· Integration ready for chat notifications

### Structure

```markdown
# DAT Security Audit Report

## Executive Summary
- **Scanned**: 245 files
- **Violations**: 12 total (0 critical, 3 high, 5 medium, 4 low)
- **Compliance**: SOC2 ✅, GDPR ✅

## Critical Findings
🚨 No critical violations detected

## High Severity Findings
### Hardcoded Secrets (3 violations)
- `src/config.py:42` - API_KEY detected
- `src/auth.py:15` - Database password in code

## File Summary
| File | Size | Violations | Status |
|------|------|------------|--------|
| src/main.py | 2.0 KB | 0 | ✅ |
| src/config.py | 1.5 KB | 2 | ❌ |

## Recommendations
1. Move secrets to environment variables
2. Implement secret scanning in CI/CD
3. Review authentication configuration
```

### Usage Examples

```bash
# Markdown for pull requests
dat . --markdown SECURITY_SCAN.md

# GitHub integration
dat . --md | gh issue create --title "Security Scan Results" --body-file -

# Chat notifications
dat . --md | curl -X POST -d @- $SLACK_WEBHOOK_URL
```

## Custom Output Formats

### Template-Based Reporting

```bash
# Custom template output
dat . --template custom-template.j2 --output custom-report.html

# Multiple format outputs
dat . --json detailed-scan.json --pdf summary-report.pdf --md quick-view.md
```

### Integration Formats

```bash
# SARIF format for GitHub Advanced Security
dat . --sarif security-results.sarif

# JUnit XML for test reporting
dat . --junit security-tests.xml

# CSV for spreadsheet analysis
dat . --csv violation-report.csv
```

## Output Configuration

### Global Output Settings

```ini
# ~/.config/dat/config.ini
[Output]
output_dir = ./reports
timestamp_format = %Y%m%d_%H%M%S
include_file_contents = false
max_content_length = 1024
compress_json = false
pdf_theme = light
pdf_executive_summary = true
default_format = jsonl
```

### Environment Variables

```bash
# Output directory
export DAT_OUTPUT_DIR=/var/log/security-scans

# Format preferences
export DAT_DEFAULT_FORMAT=json
export DAT_PDF_THEME=corporate

# Compression settings
export DAT_COMPRESS_JSON=true
```

## Atomic Writes & Integrity

### Crash-Safe Operations

All writers use temporary files and atomic renames to prevent partial writes:

```python
# Pseudo-code implementation
with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
    json.dump(report_data, tmp)
    tmp.flush()
    os.fsync(tmp.fileno)
os.replace(tmp.name, final_path)
```

### Integrity Verification

```bash
# Verify report integrity
sha256sum audit.json audit.pdf

# Check signature validity
gpg --verify audit.json.asc audit.json

# Validate JSON structure
jq . audit.json > /dev/null && echo "Valid JSON"
```

## Performance Characteristics

### Format Comparison

Format File Size Generation Speed Memory Usage Use Case
JSON Medium Fast Low CI/CD, Automation
JSONL Small Very Fast Very Low Streaming, Large Scans
PDF Large Slow High Compliance, Reports
Markdown Small Fast Low PRs, Documentation

### Optimization Tips

```bash
# For large repositories
dat . --jsonl stream.jsonl --batch-size 1000

# Memory-constrained environments
dat . --json summary.json --max-memory 512

# Fast scanning with basic output
dat . --fast --md quick-scan.md
```

## Enterprise Integration

### CI/CD Pipeline Examples

```yaml
# GitHub Actions
- name: Security Scan
  run: |
    dat . --json security-scan.json --pdf compliance-report.pdf
    # Upload artifacts
    gh release upload latest security-scan.json compliance-report.pdf

# GitLab CI
security_scan:
  script:
    - dat . --json gl-sast-report.json
  artifacts:
    reports:
      sast: gl-sast-report.json
```

### Compliance Evidence Packages

```bash
# Generate complete evidence package
dat . --from-lrc \
  --json compliance-audit.json \
  --pdf executive-report.pdf \
  --md findings-summary.md \
  --bundle-evidence \
  --sign

# Create distributable package
tar czf compliance-evidence-$(date +%Y%m%d).tar.gz \
  compliance-audit.json* \
  executive-report.pdf* \
  findings-summary.md
```

### Monitoring & Alerting Integration

```bash
#!/bin/bash
# Real-time security monitoring
dat . --jsonl - | while IFS= read -r line; do
  violation=$(echo "$line" | jq -r 'select(.type == "violation" and .severity == "critical")')
  if [ -n "$violation" ]; then
    send_alert "$violation"
  fi
done
```

## Format Conversion & Interoperability

### Cross-Format Utilities

```bash
# Convert JSON to other formats
dat --convert audit.json --to pdf --output converted.pdf

# Extract specific data
jq '.findings[] | select(.severity == "critical")' audit.json

# Generate diffs between scans
diff <(jq -S . scan1.json) <(jq -S . scan2.json)
```

### Third-Party Integration

```bash
# Import into security tools
dat . --json | jq -c '.findings[]' | nc security-log-server 514

# Dashboard integration
dat . --json | curl -X POST -H "Content-Type: application/json" -d @- $DASHBOARD_URL

# Notification systems
dat . --md | python3 send_to_slack.py
```

---

DAT's flexible output formats ensure security findings are accessible to all stakeholders—from developers reviewing pull requests to executives reviewing compliance evidence—while maintaining data integrity and enterprise-grade reliability.

