# Dev Audit Tool (DAT) v3.0.0-alpha.1

The Dev Audit Tool (DAT) is an enterprise-ready auditing engine designed to analyse source repositories, enforce policy driven
rules, and produce cryptographically signed reports. Version 3.0.0-alpha.1 introduces an asynchronous scanner, LRC integration,
and a streamlined CLI experience that remains backwards compatible with previous releases.

## Highlights

- **Modular src layout** with dedicated packages for scanning, PDF export, integration, and rules.
- **Asynchronous scanning** optimised for large repositories with optional deep/safe modes.
- **LRC aware policies** by reading schemas from `~/.config/lrc/dat_integration.json` or a custom path.
- **Standardised outputs** for JSONL and PDF including repository metadata, timestamps, and fingerprint hashes.
- **Artifact signing** using GPG when available with automatic SHA256 fallbacks.
- **Encrypted audit log** persisted to `~/.config/dat/auditlog.jsonl` using `cryptography`.
- **Interactive CLI** with colour-rich tables, diffing support, and extended flag set (`--safe`, `--deep`, `--ignore`, `--report`,
  `--diff`, `--from-lrc`).

```mermaid
digraph workflow {
  rankdir=LR;
  subgraph cluster_lrc {
    label="LRC";
    config["Integration config"];
  }
  repo["Source repository"];
  scanner["Async scanner"];
  policy["Policy engine"];
  reports["JSONL/PDF reports"];
  gpg["Signing"];
  log["Encrypted audit log"];

  config -> policy;
  repo -> scanner;
  scanner -> policy;
  policy -> reports;
  reports -> gpg;
  reports -> log;
}
```

## Quick start

```bash
# Clone and install dependencies
pip install -e .

# Or use the bundled bootstrap script
chmod +x install_deps.sh
./install_deps.sh
```

Run the CLI against the current directory:

```bash
python -m dat.cli --safe --ignore "*.pyc" --report reports/audit.jsonl
```

The default invocation (`dat`) continues to work when the project is installed via the provided `pyproject.toml` entry point.

## CLI examples

```bash
# Safe scan with PDF output and signing
dat --safe --pdf reports/audit.pdf

# Deep scan with additional ignores and baseline diffing
dat -p --ignore "node_modules" --ignore "*.log" --diff reports/audit.jsonl

# Consume LRC metadata automatically
dat --from-lrc ./repo --report reports/audit.jsonl
```

Colour output can be disabled by piping the command to a file; DAT detects non-TTY environments automatically via Rich.

## LRC integration

If the `--from-lrc` flag is provided, DAT reads the shared configuration located at
`~/.config/lrc/dat_integration.json`. A minimal configuration looks like:

```json
{
  "schemas": [
    {
      "repos": ["dat"],
      "owner": "engineering@lrc",
      "compliance": "internal-standard",
      "rules": [
        {"id": "no.todo", "patterns": ["TODO"], "severity": "medium"}
      ]
    }
  ]
}
```

Schema metadata is merged with the default DAT rules and surfaced inside JSON/PDF reports.

## Enterprise logging

Every run appends an encrypted entry to `~/.config/dat/auditlog.jsonl`. The encryption key is generated on first execution and is
stored with `0600` permissions. Use `cryptography.fernet.Fernet` to decrypt entries when authorised.

## Development

```bash
# Run the test suite
pytest

# Execute the tox matrix
tox
```

## Licensing

DAT is distributed under the MIT License. See [LICENSE](./LICENSE) for details.
