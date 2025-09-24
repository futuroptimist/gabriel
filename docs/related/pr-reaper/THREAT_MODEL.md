# pr-reaper Threat Model

pr-reaper automates the closure of stale pull requests via GitHub Actions workflows.
This document captures current assumptions and risks.

## Current Snapshot (2025-09-24)

- **Workflow:** Runs as a scheduled GitHub Action that performs dry-run analysis before
  optionally closing PRs authored by the repository owner.
- **Touchpoints:** Requires a token with `repo` scope to close PRs across multiple projects.

## Security Assumptions

- GitHub-hosted runners execute the workflow with repository-scoped tokens.
- Dry-run mode is used to validate configuration before enabling destructive actions.

## Potential Risks

- Misconfigured filters could close active or collaborative pull requests unexpectedly.
- Stored tokens or workflow secrets might be abused if workflow files are compromised.
- Lack of audit logging could make it difficult to prove which PRs were closed by automation.
