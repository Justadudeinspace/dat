# Output Formats

DAT produces three primary report formats. Each format contains the same metadata, scan statistics,
and policy findings, making it straightforward to switch consumers without modifying the pipeline.

## JSON (`--report audit.json`)

* UTF-8 encoded and newline terminated.
* Keys are sorted for deterministic diffs.
* Suitable for machine ingestion and CI gating.

## Markdown (`--report audit.md`)

* Human-readable summary with headings and bullet lists.
* Ideal for attaching to pull requests or chat notifications.
* Includes the top skipped files and rule violations.

## PDF (`--output audit.pdf`)

* Generated via ReportLab with DejaVu Sans Mono (Courier fallback).
* Layout is kept minimal to ensure fast rendering and compatibility with default viewers on every
  supported platform.
* Pair with `--sign` to produce detached ASCII signatures alongside the PDF.

### Atomic writes

All writers use temporary files and atomic renames to avoid half-written artifacts during
interruptions or concurrent runs.
