# gitshelves Threat Model

The **gitshelves** project turns GitHub contribution history into printable blocks.

## Current Snapshot (2025-10-08)

- **Operational context:** Continues to fetch GitHub contribution data, render SCAD/STL blocks, and
  ship a static viewer.
- **Key changes since 2025-09-29:** Baseplate selector feature (PR #144) broadened CLI inputs and
  refreshed GitHub Actions workflows.
- **Risks to monitor:** Validate new template arguments to avoid command injection and monitor workflow
  secrets used during STL render jobs.

## Threats

- **API abuse:** Excessive API requests or leaked tokens could trigger rate limits or account
  compromise.
- **Malicious STL:** Contributors could slip malicious geometry or macros into SCAD files.
- **Dependency risk:** npm packages used for the viewer might drift without lockfile updates.

## Mitigations

- Encourage short-lived tokens or GitHub Apps for fetching contributions.
- Keep SCAD rendering within CI and require reviewers to inspect geometry diffs.
- Update npm lockfiles regularly and run `npm audit` as part of pre-commit hooks.
