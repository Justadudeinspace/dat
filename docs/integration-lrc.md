# LRC Integration

DAT can consume metadata produced by LRC build pipelines to enrich audit results. When the
`--from-lrc` flag is provided, DAT performs the following steps:

1. Load shared defaults from `~/.config/lrc/dat_integration.json` if present.
2. Parse `<repo>/.lrc-build.json` for project specific context.
3. Merge both payloads (CLI flags take precedence) and inject the combined metadata into report
   headers.
4. Emit `<repo>/.lrc-audit.json` containing scan statistics, findings, and the merged metadata.

## Example workflow

```bash
# Ensure the integration config exists
mkdir -p ~/.config/lrc
cat > ~/.config/lrc/dat_integration.json <<'JSON'
{
  "policy": {
    "require_signing": true
  }
}
JSON

# Run DAT with enrichment
dat repo --from-lrc --report audit.json --output audit.pdf --sign
```

The generated `.lrc-audit.json` mirrors the JSON report format and can be archived alongside LRC build
artifacts.

## Handling missing metadata

If `.lrc-build.json` is absent, DAT completes the scan using defaults and still writes the audit file
with the available metadata. Errors are surfaced via non-zero exit codes and console warnings in
verbose mode.
