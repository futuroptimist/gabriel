# gitshelves Threat Model

The **gitshelves** project turns GitHub contribution history into printable blocks.

## Current Snapshot (2025-09-29)

- **Operational context:** Fetches GitHub contribution data, renders SCAD/STL assets, and ships an
  optional viewer for previewing models.
- **Key changes since 2025-09-24:** Prompt docs now sit under `docs/prompts/codex/`; CLI and tests
  were refreshed without altering API scopes.
- **Risks to monitor:** GitHub API usage with personal access tokens and the integrity of generated
  STL files.

## Threats

- **API abuse:** Excessive API requests or leaked tokens could trigger rate limits or account
  compromise.
- **Malicious STL:** Contributors could slip malicious geometry or macros into SCAD files.
- **Dependency risk:** npm packages used for the viewer might drift without lockfile updates.

## Mitigations

- Encourage short-lived tokens or GitHub Apps for fetching contributions.
- Keep SCAD rendering within CI and require reviewers to inspect geometry diffs.
- Update npm lockfiles regularly and run `npm audit` as part of pre-commit hooks.
