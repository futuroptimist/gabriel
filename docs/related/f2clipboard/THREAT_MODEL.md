# f2clipboard Threat Model

The **f2clipboard** project turns Codex task pages and GitHub logs into clipboard-ready summaries.

## Current Snapshot (2025-10-18)

- **Operational context:** Python CLI and GitHub Action variants scrape task metadata, normalize logs,
  and render plaintext summaries for downstream tooling.
- **Key changes since 2025-09-29:** Major CLI rebuild (PR #162) added plugin architecture, secret
  helpers, and new docs covering polish initiatives; the action now ships richer configuration.
- **Risks to monitor:** Secret handling within plugins, cached task transcripts on disk, and GitHub
  personal access tokens used for API calls.

## Threats

- **Credential leakage:** CLI plugins might read tokens from `.env` and accidentally log them.
- **Data exposure:** Persisted task HTML or CLI output could leak sensitive repo information.
- **Supply chain:** Dependencies declared in `pyproject.toml` and action composite steps could pull
  malicious updates.

## Mitigations

- Encourage temporary tokens and document purge commands for cached transcripts.
- Keep pre-commit hooks scanning for secrets (`scripts/checks.sh`) and run them in CI.
- Pin dependency versions and use Dependabot to surface critical upgrades quickly.
