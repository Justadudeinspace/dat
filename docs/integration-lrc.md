# LRC Integration for Enterprise Auditing

DAT seamlessly integrates with LRC (License and Regulatory Compliance) build pipelines to enrich audit results with enterprise metadata and policies. When the `--from-lrc` flag is provided, DAT performs intelligent metadata aggregation and policy enforcement.

## Integration Workflow

### Basic Usage
```bash
# Enable LRC integration with auto-detection
dat repo --from-lrc

# Specify custom LRC configuration path
dat repo --from-lrc /path/to/lrc-config.json

# Full enterprise workflow with reporting and signing
dat repo --from-lrc --report audit.json --output audit.pdf --sign

# Compliance scanning with specific frameworks
dat repo --from-lrc --compliance soc2,gdpr,hipaa --verbose
```

### Advanced Integration

```bash
# Multiple compliance frameworks
dat repo --from-lrc --compliance soc2,gdpr,hipaa,pcidss,iso27001

# Evidence collection for audits
dat repo --from-lrc --bundle-evidence --output-dir ./compliance-evidence

# Pre-approval validation
dat repo --from-lrc --pre-approval-check --json pre-approval-scan.json
```

## Configuration Setup

### LRC Configuration Structure

```bash
# Create LRC configuration directory
mkdir -p ~/.config/lrc

# Generate comprehensive LRC configuration
cat > ~/.config/lrc/dat_integration.json << 'JSON'
{
  "policy": {
    "require_signing": true,
    "max_critical_violations": 0,
    "max_high_violations": 5,
    "audit_retention_days": 90,
    "require_approval": false,
    "auto_escalate_critical": true,
    "compliance_frameworks": ["soc2", "gdpr", "hipaa"]
  },
  "schemas": [
    {
      "repos": ["dat", "enterprise-.*"],
      "owner": "security-team@company.com",
      "compliance": ["soc2", "gdpr"],
      "tags": ["production", "pci-dss", "hipaa-compliant"],
      "rules": [
        {
          "id": "lrc.no-secrets",
          "patterns": ["SECRET=", "API_KEY=", "PRIVATE_KEY=", "ENCRYPTION_KEY="],
          "severity": "critical",
          "description": "Hardcoded secrets detected",
          "category": "security",
          "compliance": ["soc2", "gdpr"]
        },
        {
          "id": "lrc.credentials",
          "patterns": ["password\\s*=", "pwd\\s*=", "credential\\s*="],
          "severity": "critical", 
          "description": "Hardcoded credentials",
          "category": "security"
        }
      ]
    },
    {
      "repos": ["web-.*", "frontend-.*"],
      "owner": "web-team@company.com",
      "compliance": ["gdpr"],
      "rules": [
        {
          "id": "lrc.gdpr.pii",
          "patterns": ["email@", "phone", "address", "ssn", "credit.card"],
          "severity": "high",
          "description": "Potential PII exposure",
          "category": "compliance"
        }
      ]
    }
  ],
  "metadata": {
    "organization": "Acme Corporation",
    "division": "Engineering",
    "contact": "security@acme.com",
    "version": "1.0.0",
    "valid_until": "2024-12-31"
  }
}
JSON
```

### Repository Build Metadata

```json
// .lrc-build.json
{
  "project": "production-service",
  "version": "2.1.0",
  "build_id": "build-20240525-001",
  "commit_hash": "a1b2c3d4e5f67890123456789abcdef01234567",
  "branch": "main",
  "build_timestamp": "2024-05-25T10:30:00Z",
  "artifacts": ["app.jar", "docs.zip", "config.yaml"],
  "dependencies": ["spring-boot:2.7.0", "log4j:2.17.0", "postgresql:42.5.0"],
  "environment": "production",
  "team": "backend-services",
  "compliance_requirements": ["soc2", "gdpr"]
}
```

## Integration Architecture

### Metadata Loading Sequence

1. Global Configuration: Loads ~/.config/lrc/dat_integration.json (configurable via LRC_CONFIG_PATH)
2. Project Context: Parses <repository>/.lrc-build.json for build-specific metadata
3. CLI Overrides: Command-line arguments take precedence over configuration files
4. Audit Output: Generates <repository>/.lrc-audit.json with comprehensive scan results

### File Locations and Precedence

```
~/.config/lrc/dat_integration.json    # Global defaults (lowest priority)
<repo>/.lrc-build.json                # Project-specific (medium priority)  
CLI arguments                         # Runtime overrides (highest priority)
```

### Environment Configuration

```bash
# Custom LRC configuration path
export LRC_CONFIG_PATH=/etc/enterprise/lrc/dat_config.json

# Compliance framework overrides
export DAT_COMPLIANCE_FRAMEWORKS="soc2,gdpr,hipaa"

# Enterprise metadata
export DAT_ORGANIZATION="Acme Corp"
export DAT_COMPLIANCE_CONTACT="security@acme.com"
```

## Configuration Schema

### Global Configuration (dat_integration.json)

```json
{
  "policy": {
    "require_signing": true,
    "max_critical_violations": 0,
    "max_high_violations": 5,
    "audit_retention_days": 90,
    "require_approval": false,
    "auto_escalate_critical": true,
    "compliance_frameworks": ["soc2", "gdpr", "hipaa", "pcidss", "iso27001"],
    "evidence_retention_days": 365,
    "auto_bundle_evidence": true
  },
  "schemas": [
    {
      "repos": ["dat", "enterprise-.*"],
      "owner": "security-team",
      "compliance": ["soc2", "hipaa", "gdpr"],
      "tags": ["production", "pci-dss"],
      "rules": [
        {
          "id": "lrc.custom-rule",
          "patterns": ["password\\s*=", "token\\s*:", "secret\\s*="],
          "severity": "high",
          "description": "Hardcoded credentials",
          "category": "security",
          "compliance": ["soc2", "gdpr"],
          "remediation": "Use environment variables or secure secret management"
        }
      ]
    }
  ],
  "metadata": {
    "organization": "Acme Corp",
    "division": "Engineering",
    "contact": "security@acme.com",
    "version": "1.0.0",
    "valid_until": "2024-12-31"
  }
}
```

### Build Metadata (.lrc-build.json)

```json
{
  "build_id": "build-12345",
  "commit_hash": "a1b2c3d4",
  "branch": "main",
  "version": "1.2.3",
  "build_timestamp": "2024-01-15T10:30:00Z",
  "artifacts": ["app.jar", "docs.zip"],
  "dependencies": ["spring-boot:2.7.0", "log4j:2.17.0"],
  "environment": "production",
  "team": "backend-services",
  "compliance_requirements": ["soc2", "gdpr"],
  "security_contact": "security@company.com",
  "deployment_region": "us-east-1"
}
```

# Rule Engine Enhancements

## Rule Specification

### Each rule must contain:

· id – Unique identifier (prefixed with lrc. for custom rules)
· patterns – String, regex pattern, or list of patterns
· severity – critical, high, medium, low, info (default: medium)
· description – Human-readable explanation (optional but recommended)
· category – security, compliance, quality, custom (optional)
· compliance – Applicable compliance frameworks (optional)
· remediation – Suggested fix (optional)

### Pattern Types

```json
{
  "rules": [
    {
      "id": "lrc.secret-detection",
      "patterns": ["SECRET=", "API_KEY\\s*=", "PRIVATE_KEY\\s*="],
      "severity": "critical",
      "description": "Hardcoded secrets detection",
      "category": "security",
      "compliance": ["soc2", "gdpr"]
    },
    {
      "id": "lrc.license-check", 
      "patterns": ["GPL-", "AGPL-", "proprietary"],
      "severity": "high",
      "description": "Restricted license header",
      "category": "compliance"
    },
    {
      "id": "lrc.pii.detection",
      "patterns": ["email@", "phone", "address", "ssn", "credit.card"],
      "severity": "high",
      "description": "Potential PII exposure",
      "category": "compliance",
      "compliance": ["gdpr", "hipaa"]
    }
  ]
}
```

### Rule Merging Behavior

· LRC rules augment default DAT policies
· Rules with duplicate IDs override built-in rules
· Severity escalation is supported but not de-escalation
· Pattern matching uses case-sensitive substring search by default
· Compliance mapping links violations to specific frameworks

## Audit Output

### Generated Audit File (.lrc-audit.json)

```json
{
  "metadata": {
    "timestamp": "2024-01-15T10:35:22Z",
    "dat_version": "3.0.0-alpha.1",
    "scanner": "DAT Enterprise",
    "lrc_integration": {
      "config_source": "~/.config/lrc/dat_integration.json",
      "build_source": ".lrc-build.json",
      "schema_applied": "enterprise-security",
      "compliance_frameworks": ["soc2", "gdpr"]
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
    "compliance_frameworks": ["soc2", "gdpr"],
    "evidence_generated": true
  },
  "findings": [
    {
      "rule_id": "lrc.no-secret",
      "file": "src/config.py",
      "line": 42,
      "severity": "critical",
      "message": "Hardcoded secret detected",
      "context": "API_KEY='sk_live_12345'",
      "category": "security",
      "compliance": ["soc2", "gdpr"],
      "remediation": "Use environment variables for sensitive data"
    }
  ],
  "build_context": {
    "build_id": "build-12345",
    "commit_hash": "a1b2c3d4",
    "version": "1.2.3",
    "environment": "production"
  },
  "compliance_evidence": {
    "soc2": {
      "status": "compliant",
      "violations": 0,
      "evidence_files": ["soc2-controls.json", "access-logs.csv"]
    },
    "gdpr": {
      "status": "compliant", 
      "violations": 1,
      "evidence_files": ["pii-scan.json", "data-flow.pdf"]
    }
  }
}
```

## Error Handling and Recovery

### Graceful Degradation

· Missing config file: Proceeds with default policies, logs warning
· Invalid JSON: Falls back to defaults, reports error with details
· Missing build metadata: Uses available context, continues scan
· Network failures: Continues with cached policies if available
· Permission issues: Skips restricted files, logs access errors

### Exit Codes

· 0: Success with full LRC integration
· 1: General error (file not found, permissions)
· 2: Configuration error (invalid JSON, schema violation)
· 3: Policy violation (exceeds max critical violations)
· 4: Integration partial failure (proceeds with defaults)
· 5: Compliance failure (framework requirements not met)

### Debugging Integration

```bash
# Verbose output for troubleshooting
dat repo --from-lrc --verbose

# Debug configuration loading
DAT_DEBUG=1 dat repo --from-lrc

# Validate configuration without scanning
dat repo --from-lrc --validate-config

# Test specific compliance frameworks
dat repo --from-lrc --compliance soc2 --test-mode

# Generate integration report
dat repo --from-lrc --integration-report integration-debug.json
```

## Enterprise Features

### Compliance Reporting

· SOC2, GDPR, HIPAA, PCI-DSS, ISO27001 metadata tracking
· Automated evidence collection for audits
· Retention policy enforcement (90 days default)
· Framework-specific reporting and validation

### Security Enhancements

· Artifact signing verification with GPG
· Tamper-evident audit logs with cryptographic hashes
· Cryptographic integrity checks for all outputs
· Access control validation for sensitive files

### Integration Hooks

```bash
# Pre-scan validation
dat repo --from-lrc --pre-scan-check

# Post-scan compliance check
dat repo --from-lrc --compliance-check

# Generate compliance evidence bundle
dat repo --from-lrc --bundle-evidence

# Compliance framework validation
dat repo --from-lrc --validate-compliance soc2,gdpr

# Evidence package generation
dat repo --from-lrc --evidence-package ./compliance-evidence
```

## CI/CD Integration Examples

### GitHub Actions

```yaml
- name: LRC Compliance Scan
  env:
    LRC_CONFIG_PATH: .github/lrc-config.json
    DAT_SIGNING_KEY: ${{ secrets.GPG_SIGNING_KEY }}
  run: |
    dat . --from-lrc --compliance soc2,gdpr \
          --json compliance-scan.json \
          --pdf compliance-report.pdf \
          --sign
    # Fail on critical violations
    if [ $? -eq 3 ]; then
      echo "Critical compliance violations detected"
      exit 1
    fi
```

### GitLab CI

```yaml
compliance_scan:
  variables:
    LRC_CONFIG_PATH: ".gitlab/lrc-config.json"
  script:
    - dat . --from-lrc --compliance soc2,gdpr --json scan.json
  artifacts:
    paths:
      - scan.json
      - .lrc-audit.json
    reports:
      sast: scan.json
```

### Jenkins Pipeline

```groovy
stage('Compliance Audit') {
  steps {
    script {
      sh '''
        dat . --from-lrc --compliance soc2,gdpr \
              --json compliance-scan.json \
              --pdf compliance-report.pdf \
              --bundle-evidence
      '''
      // Archive compliance evidence
      archiveArtifacts artifacts: 'compliance-evidence/**/*', fingerprint: true
    }
  }
}
```

## Best Practices

### Repository Setup

```bash
# Include in CI/CD pipeline
- name: Security Audit
  run: dat . --from-lrc --report audit.json --sign

# Fail build on critical violations  
- name: Compliance Check
  run: |
    dat . --from-lrc --no-critical-violations
    if [ $? -eq 3 ]; then
      echo "Critical violations detected - failing build"
      exit 1
    fi

# Regular compliance scanning
- name: Scheduled Compliance Scan
  run: |
    dat . --from-lrc --compliance soc2,gdpr,hipaa \
          --json scheduled-scan-$(date +%Y%m%d).json \
          --pdf compliance-report-$(date +%Y%m%d).pdf
```

### Configuration Management

· Use environment-specific configuration files
· Implement configuration versioning with semantic versioning
· Regular policy reviews and updates (quarterly recommended)
· Automated configuration validation in CI/CD pipelines
· Backup and recovery procedures for LRC configurations
· Access control for sensitive compliance settings

### Evidence Management

```bash
# Generate comprehensive evidence package
dat . --from-lrc --bundle-evidence --output-dir ./compliance-evidence

# Include in release artifacts
tar czf compliance-evidence-$(date +%Y%m%d).tar.gz compliance-evidence/

# Upload to secure storage
aws s3 cp compliance-evidence-*.tar.gz s3://compliance-bucket/evidence/
```

### Monitoring and Alerting

```bash
#!/bin/bash
# Compliance monitoring script
COMPLIANCE_SCAN="compliance-scan-$(date +%Y%m%d).json"

dat . --from-lrc --json "$COMPLIANCE_SCAN"

# Check for critical violations
CRITICAL_VIOLATIONS=$(jq '.summary.critical_violations' "$COMPLIANCE_SCAN")

if [ "$CRITICAL_VIOLATIONS" -gt 0 ]; then
  # Send alert
  curl -X POST -H "Content-Type: application/json" \
    -d "{\"text\": \"Critical compliance violations detected: $CRITICAL_VIOLATIONS\"}" \
    "$SLACK_WEBHOOK_URL"
fi
```

---

LRC integration transforms DAT from a security scanner into a comprehensive compliance automation platform, providing enterprise-grade auditing with regulatory framework support.
