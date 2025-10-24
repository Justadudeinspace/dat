# Continuous Integration

DAT ships with GitHub Actions workflows covering quality gates and release signing.

## ci.yml

Located at `.github/workflows/ci.yml`, this workflow performs the following steps on pushes and pull
requests:

1. Set up Python 3.11.
2. Install project and development dependencies.
3. Run code style tools (`black`, `isort`, `mypy`).
4. Execute the pytest suite with coverage and archive the HTML report as an artifact.
5. Optionally run a smoke PDF generation test on Ubuntu runners.

## sign-and-release.yml

Triggered when a git tag matching `v*` is pushed. The workflow:

1. Builds the wheel and source distribution.
2. Generates JSON, Markdown, and PDF sample reports.
3. Signs the artifacts using GPG (the workflow expects a secret key and passphrase in GitHub
   secrets).
4. Publishes a GitHub Release with the signed assets attached.

Refer to the workflow files for exact implementation details and adjust environment secrets before
enabling them in production.
