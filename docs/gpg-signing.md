# GPG Signing

DAT provides comprehensive cryptographic signing capabilities for audit reports and artifacts using GNU Privacy Guard (GPG). Enable signing with the `--sign` flag or configure persistent signing policies in your configuration.

## Requirements

### System Requirements
- **GPG Installation**: `gpg` must be available on `PATH`
- **Key Configuration**: A default key should be configured (`gpg --list-secret-keys`)
- **Permissions**: Appropriate access to keyring and configuration

### Key Management
```bash
# Check available keys
gpg --list-secret-keys

# Generate new key (if none exists)
gpg --full-generate-key

# Import existing key
gpg --import private-key.asc
```

## Usage

### Basic Signing

```bash
# Sign all generated reports
dat . --sign --report audit.json --output audit.pdf

# Sign specific formats only
dat . --sign --json signed-audit.json --pdf signed-report.pdf

# Disable signing explicitly
dat . --no-sign --report audit.json
```

### Enterprise Signing Configuration

```ini
# ~/.config/dat/config.ini
[Security]
require_signing = true

[Enterprise]
organization_name = "Acme Corporation"
```

### LRC-Integrated Signing

```json
{
  "policy": {
    "require_signing": true,
    "signing_key": "security-team@company.com"
  },
  "schemas": [
    {
      "repos": ["production-.*"],
      "require_signed_artifacts": true
    }
  ]
}
```

## Output Artifacts

### When signing is enabled, DAT produces:

```
audit.json          # Original report
audit.json.asc      # Detached ASCII signature
audit.pdf           # PDF report  
audit.pdf.asc       # PDF signature
dat-report.jsonl    # JSON Lines report
dat-report.jsonl.asc # JSON Lines signature
```

## Advanced Signing Features

### Key Selection

```bash
# Use specific key by ID
export DAT_SIGNING_KEY=ABCD1234
dat . --sign --report audit.json

# Key by email
export DAT_SIGNING_KEY=security@company.com
dat . --sign

# Key fingerprint
export DAT_SIGNING_KEY=0x1A2B3C4D5E6F7G8H
```

### CI/CD Integration

```yaml
# GitHub Actions example
- name: Security Audit with Signing
  env:
    DAT_SIGNING_KEY: ${{ secrets.GPG_SIGNING_KEY }}
  run: |
    dat . --from-lrc --sign --report audit.json
    gpg --verify audit.json.asc audit.json

# GitLab CI example
security_scan:
  variables:
    DAT_SIGNING_KEY: "${GPG_KEY_ID}"
  script:
    - dat . --sign --json security-scan.json
    - gpg --verify security-scan.json.asc security-scan.json
  artifacts:
    paths:
      - security-scan.json
      - security-scan.json.asc
```

### Automated Key Management

```bash
# Key rotation script
#!/bin/bash
# Rotate signing keys
OLD_KEY="ABCD1234"
NEW_KEY="EFGH5678"

# Update configuration
sed -i "s/$OLD_KEY/$NEW_KEY/" ~/.config/dat/config.ini
export DAT_SIGNING_KEY="$NEW_KEY"

# Test new key
dat . --sign --report test-audit.json
gpg --verify test-audit.json.asc test-audit.json
```

## Signature Verification

### Manual Verification

```bash
# Verify PDF signature
gpg --verify audit.pdf.asc audit.pdf

# Verify JSON signature  
gpg --verify audit.json.asc audit.json

# Verify with specific key
gpg --keyring ./company-keys.gpg --verify audit.pdf.asc audit.pdf
```

### Automated Verification

```bash
#!/bin/bash
# Automated verification script
verify_signature() {
    local file="$1"
    local signature="${file}.asc"
    
    if [ ! -f "$signature" ]; then
        echo "❌ Missing signature for $file"
        return 1
    fi
    
    if gpg --verify "$signature" "$file" 2>/dev/null; then
        echo "✅ Signature valid: $file"
        return 0
    else
        echo "❌ Signature invalid: $file"
        return 1
    fi
}

# Verify all signed artifacts
for file in *.json *.pdf *.jsonl; do
    if [ -f "$file" ]; then
        verify_signature "$file"
    fi
done
```

### Public Key Distribution

```bash
# Export public key for distribution
gpg --export -a "Security Team" > security-team-public.asc

# Share with downstream teams
echo "Public key for verification:" > VERIFICATION.md
cat security-team-public.asc >> VERIFICATION.md

# Include in release artifacts
cp security-team-public.asc release-artifacts/
```

## Error Handling

### Graceful Degradation

```bash
# If signing fails, continue without signatures
dat . --sign  # If GPG unavailable, continues with warning

# Force failure on signing errors
dat . --sign --require-signing
```

## Common Issues and Solutions

### Missing GPG

```bash
# Install GPG
# Ubuntu/Debian
sudo apt-get install gnupg

# macOS  
brew install gnupg

# Windows
choco install gnupg
```

### No Default Key

```bash
# Generate a new key
gpg --full-generate-key

# Or set specific key
export DAT_SIGNING_KEY=$(gpg --list-secret-keys --with-colons | grep ^sec | cut -d: -f5 | head -1)
```

### Permission Issues

```bash
# Fix keyring permissions
chmod 700 ~/.gnupg
chmod 600 ~/.gnupg/*

# Ensure proper access
gpg --list-keys  # Test access
```

## Security Best Practices

### Key Security

```bash
# Use hardware security modules when available
gpg --card-status

# Set appropriate key expiration
gpg --edit-key KEY_ID
> expire
> 1y  # Set 1-year expiration

# Regular key rotation
# Rotate keys every 6-12 months
```

### Verification Policies

```ini
# Organization security policy
[Security]
require_signing = true
signature_verification = required
trusted_keys = /etc/dat/trusted-keys.gpg

[Enterprise]
signing_policy = strict
key_rotation_days = 180
```

### Audit Trail

```bash
# Log signing activities
dat . --sign --audit-logging

# Verify audit trail integrity
gpg --verify audit-log.jsonl.asc audit-log.jsonl
```

## Integration Examples

### Development Workflow

```bash
#!/bin/bash
# Pre-commit hook with signing
if dat . --sign --report pre-commit-scan.json; then
    echo "✅ Security scan passed and signed"
    git add pre-commit-scan.json pre-commit-scan.json.asc
else
    echo "❌ Security scan failed"
    exit 1
fi
```

### Release Process

```bash
#!/bin/bash
# Release signing script
VERSION="1.0.0"
export DAT_SIGNING_KEY="$RELEASE_SIGNING_KEY"

dat . --deep --sign \
    --json "release-${VERSION}.json" \
    --pdf "release-${VERSION}.pdf" \
    --md "release-${VERSION}.md"

# Verify all signatures
for artifact in release-${VERSION}.*; do
    if [[ "$artifact" != *.asc ]]; then
        gpg --verify "${artifact}.asc" "$artifact" || exit 1
    fi
done

echo "✅ Release artifacts signed and verified"
```

### Compliance Evidence

```bash
#!/bin/bash
# Generate signed compliance evidence
COMPLIANCE_DATE=$(date +%Y%m%d)

dat . --from-lrc --sign --audit \
    --json "compliance-${COMPLIANCE_DATE}.json" \
    --pdf "compliance-report-${COMPLIANCE_DATE}.pdf"

# Create evidence package
tar czf "compliance-evidence-${COMPLIANCE_DATE}.tar.gz" \
    compliance-${COMPLIANCE_DATE}.json \
    compliance-${COMPLIANCE_DATE}.json.asc \
    compliance-report-${COMPLIANCE_DATE}.pdf \
    compliance-report-${COMPLIANCE_DATE}.pdf.asc

echo "✅ Signed compliance evidence generated"
```

## Troubleshooting

### Debugging Signing Issues

```bash
# Enable verbose signing output
DAT_DEBUG=1 dat . --sign --verbose

# Test GPG independently
echo "test" | gpg --clearsign

# Check key availability
gpg --list-secret-keys --keyid-format LONG
```

### Common Error Messages

```
❌ gpg: signing failed: No secret key
  Solution: Set DAT_SIGNING_KEY or configure default key

❌ gpg: no valid OpenPGP data found
  Solution: Check signature file integrity

❌ gpg: Can't check signature: No public key
  Solution: Import the public key for verification
```

## Advanced Features

### Multiple Signatures

```bash
# Sign with multiple keys (enterprise requirement)
for key in "team@company.com" "security@company.com"; do
    DAT_SIGNING_KEY="$key" dat . --sign --json "audit-${key}.json"
done
```

### Timestamp Services

```bash
# Add timestamp to signatures (RFC 3161)
gpg --output audit.json.asc --detach-sign --timestamp audit.json
```

### Smart Card Integration

```bash
# Use smart card for signing
gpg --card-edit
> admin
> key-attr
> change expiration
> quit

DAT_SIGNING_KEY=$(gpg --card-status --with-colons | grep ^pub | cut -d: -f5)
```

---

GPG signing ensures the integrity and authenticity of security audit artifacts, providing cryptographic proof of scan results and compliance evidence.

