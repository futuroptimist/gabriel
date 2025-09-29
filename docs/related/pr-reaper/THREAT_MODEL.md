# pr-reaper Threat Model

The **pr-reaper** tool automates closing stale pull requests in bulk.

## Current Snapshot (2025-09-29)

- **Operational context:** Runs as a CLI or GitHub Action that iterates through repositories using a
  personal access token.
- **Key changes since 2025-09-24:** New workflows and docs formalized automation; functionality
  remains focused on GitHub API interactions.
- **Risks to monitor:** Token scopes for closing PRs, rate-limit handling, and ensuring dry-run mode
  stays default.

## Threats

- **Token misuse:** Leaked PATs could let attackers close or modify PRs.
- **Mass closure accidents:** Misconfigured filters may close active PRs.
- **Workflow escalation:** GitHub Actions might gain write access beyond intention.

## Mitigations

- Encourage fine-grained PATs or GitHub Apps with repository-specific scopes.
- Keep dry-run mode on by default and require explicit confirmation for destructive runs.
- Log actions to provide audit trails when sweeping PRs.
