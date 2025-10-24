# GPG Signing

DAT can sign generated reports using GNU Privacy Guard (GPG). Enable signing with the `--sign` flag
or via integration defaults supplied in `~/.config/lrc/dat_integration.json`.

## Requirements

* `gpg` must be available on `PATH`.
* A default key should be configured (`gpg --list-secret-keys`).

## Usage

```bash
dat repo --report audit.json --output audit.pdf --sign
```

The command above produces `audit.json`, `audit.pdf`, and corresponding `.asc` files containing
detached ASCII signatures.

If signing fails (for example, when no key is available) DAT prints a warning but continues the run.
Inspect the return code in CI pipelines to decide whether unsigned reports should fail the build.

## Verifying signatures

```bash
gpg --verify audit.pdf.asc audit.pdf
```

The same command works for JSON artifacts. Store the public keys (for example in
`jadis_publickey.asc`) alongside release assets to simplify verification for downstream teams.
