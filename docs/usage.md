# DAT Usage Guide

The Dev Audit Tool exposes a single `dat` command that accepts a repository path and a collection of
flags to tailor the analysis. This document expands on the quickstart examples from the README.

## Basic invocation

```bash
dat . --report audit.json
```

The command above scans the current directory, honours the default safe thresholds (10 MiB / 1000
lines), and writes a deterministic JSON report to `audit.json`.

## Ignoring files

Provide `-i/--ignore` multiple times to suppress paths via glob patterns:

```bash
dat /src/project --ignore "node_modules" --ignore "*.pyc"
```

The ignore logic applies to directories and files alike.

## Safe vs deep mode

`--safe` is enabled automatically. For large binary heavy repositories, disable it or enable `--deep`
which performs an unrestricted scan:

```bash
# Disable safe mode but keep default thresholds
dat repo --no-safe

# Fully deep scan
dat repo --deep --no-safe
```

Deep mode reads every file regardless of size or line count and is best paired with CI runners.

## Diffing reports

Use `--diff` to compare the current run with a previous JSON report:

```bash
dat repo --report audit.json --diff baseline.json
```

When differences are detected, DAT prints a warning to stdout. Store the generated `audit.json`
artifacts in CI to establish baselines.

## Verbose output

Add `-v/--verbose` to log summary statistics at the end of the run.
