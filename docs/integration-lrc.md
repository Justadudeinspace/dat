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
```

## Configuration Setup

```bash
# Ensure the integration config exists
mkdir -p ~/.config/lrc
cat > ~/.config/lrc/dat_integration.json <<'JSON'
{
  "policy": {
    "require_signing": true,
    "max_critical_violations": 0,
    "audit_retention_days": 90
  },
  "schemas": [
    {
      "repos": ["dat", "enterprise-.*"],
      "owner": "lrc-platform",
      "compliance": ["soc2", "gdpr"],
      "rules": [
        {
          "id": "lrc.no-secret",
          "patterns": ["SECRET=", "API_KEY=", "PRIVATE_KEY="],
          "severity": "critical",
          "description": "Hardcoded secrets detected"
        }
      ]
    }
  ]
}
JSON
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

## Configuration Schema

### Global Configuration (dat_integration.json)

```json
{
  "policy": {
    "require_signing": true,
    "max_critical_violations": 0,
    "max_high_violations": 5,
    "audit_retention_days": 90,
    "require_approval": false
  },
  "schemas": [
    {
      "repos": ["dat", "enterprise-.*"],  # Regex patterns supported
      "owner": "security-team",
      "compliance": ["soc2", "hipaa", "gdpr"],
      "tags": ["production", "pci-dss"],
      "rules": [
        {
          "id": "lrc.custom-rule",
          "patterns": ["password\\s*=", "token\\s*:"],
          "severity": "high",
          "description": "Hardcoded credentials",
          "category": "security"
        }
      ]
    }
  ],
  "metadata": {
    "organization": "Acme Corp",
    "division": "Engineering",
    "contact": "security@acme.com"
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
  "dependencies": ["spring-boot:2.7.0", "log4j:2.17.0"]
}
```

## Rule Engine Enhancements

### Rule Specification

Each rule must contain:

· id – Unique identifier (prefixed with lrc. for custom rules)
· patterns – String, regex pattern, or list of patterns
· severity – critical, high, medium, low, info (default: medium)
· description – Human-readable explanation (optional but recommended)
· category – security, compliance, quality, custom (optional)

Pattern Types

```json
{
  "rules": [
    {
      "id": "lrc.secret-detection",
      "patterns": ["SECRET=", "API_KEY\\s*="],  // Mixed literal and regex
      "severity": "critical"
    },
    {
      "id": "lrc.license-check", 
      "patterns": ["GPL-", "AGPL-"],
      "severity": "high",
      "description": "Restricted license detected"
    }
  ]
}
```

### Rule Merging Behavior

· LRC rules augment default DAT policies
· Rules with duplicate IDs override built-in rules
· Severity escalation is supported but not de-escalation
· Pattern matching uses case-sensitive substring search by default

## Audit Output

Generated Audit File (.lrc-audit.json)

```json
{
  "metadata": {
    "timestamp": "2024-01-15T10:35:22Z",
    "dat_version": "3.0.0-alpha.1",
    "scanner": "DAT Enterprise",
    "lrc_integration": {
      "config_source": "~/.config/lrc/dat_integration.json",
      "build_source": ".lrc-build.json",
      "schema_applied": "enterprise-security"
    }
  },
  "summary": {
    "scanned_files": 245,
    "total_violations": 12,
    "critical_violations": 0,
    "high_violations": 3,
    "compliance_status": "compliant"
  },
  "findings": [
    {
      "rule_id": "lrc.no-secret",
      "file": "src/config.py",
      "line": 42,
      "severity": "critical",
      "message": "Hardcoded secret detected",
      "context": "API_KEY='sk_live_12345'"
    }
  ],
  "build_context": {
    "build_id": "build-12345",
    "commit_hash": "a1b2c3d4"
  }
}
```

## Error Handling and Recovery

Graceful Degradation

· Missing config file: Proceeds with default policies, logs warning
· Invalid JSON: Falls back to defaults, reports error with details
· Missing build metadata: Uses available context, continues scan
· Network failures: Continues with cached policies if available

Exit Codes

· 0: Success with full LRC integration
· 1: General error (file not found, permissions)
· 2: Configuration error (invalid JSON, schema violation)
· 3: Policy violation (exceeds max critical violations)
· 4: Integration partial failure (proceeds with defaults)

Debugging Integration

```bash
# Verbose output for troubleshooting
dat repo --from-lrc --verbose

# Debug configuration loading
DAT_DEBUG=1 dat repo --from-lrc

# Validate configuration without scanning
dat repo --from-lrc --validate-config
```

## Enterprise Features

Compliance Reporting

· SOC2, GDPR, HIPAA, PCI-DSS metadata tracking
· Automated evidence collection for audits
· Retention policy enforcement (90 days default)

Security Enhancements

· Artifact signing verification
· Tamper-evident audit logs
· Cryptographic integrity checks

Integration Hooks

```bash
# Pre-scan validation
dat repo --from-lrc --pre-scan-check

# Post-scan compliance check  
dat repo --from-lrc --compliance-check

# Generate compliance evidence bundle
dat repo --from-lrc --bundle-evidence
```

## Best Practices

Repository Setup

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
```

Configuration Management

· Use environment-specific configuration files
· Implement configuration versioning
· Regular policy reviews and updates
· Automated configuration validation

