# DAT usage guide

The DAT CLI exposes a modern flag set while remaining compatible with older invocations. This guide highlights the most common
workflows introduced in v3.0.0-alpha.1.

## Basic scan

```bash
dat
```

Runs a safe scan against the current working directory and writes `dat-report.jsonl` alongside the repository.

## Safe vs deep mode

- `--safe` (or `-s`) skips large files (>1 MB by default) and binary assets.
- `--deep` (or `-p`) inspects all file types. Combine both flags to keep the size guard while analysing binaries.

## Ignore patterns

```bash
dat --ignore "*.pyc" --ignore "node_modules/"
```

Patterns support `fnmatch` style wildcards and are evaluated relative to the repository root.

## Reports

| Flag | Description |
| ---- | ----------- |
| `-o, --report` | Auto-detect format from extension (`.jsonl`, `.json`, `.pdf`). |
| `--jsonl` | Force JSONL output to a custom path. |
| `--pdf` | Write an additional PDF artefact. |

All reports include the repository fingerprint, timestamp, and resolved LRC metadata when available.

## Diffing results

Use `--diff <path>` to compare against a previous JSON(L) report. DAT prints a regression table when the number of rule
violations increases for tracked files.

## Interactive mode

`--interactive` prompts before scanning the repository, which is useful when working inside CI shells or sensitive environments.

## Signing

By default DAT attempts to GPG-sign every produced artefact and falls back to writing a `.asc` file containing a SHA256 digest.
Disable signing with `--no-sign`.

## Environment variables

- `LRC_CONFIG_PATH` – override the default LRC configuration location.
- `DAT_CONFIG_DIR` – override the encrypted audit log directory.

## Troubleshooting

- Ensure `gpg` is installed when hardware signing is required.
- On systems without `libmagic`, python-magic falls back to mimetype detection but may be less accurate.
- Delete `~/.config/dat/auditlog.key` to rotate the encryption key (previous log entries become unreadable).
