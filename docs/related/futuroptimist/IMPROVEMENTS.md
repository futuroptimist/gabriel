# Suggested Improvements for futuroptimist

This document aggregates enhancement ideas for the
[futuroptimist/futuroptimist](https://github.com/futuroptimist/futuroptimist) repository.

## Current Snapshot (2025-10-18)

- **Status:** ✅ (README roster refreshed 2025-10-18 23:02 UTC and still reporting green CI).
- **Stack:** Python 3.12+ utilities orchestrated with `uv`, Markdown playbooks, and lightweight
  Node 18 scripts wired through GitHub Actions for lint, docs, and coverage.
- **Conventions:** Automation prompts stay under `docs/prompts/codex/`, incident retros are logged in
  `outages/`, and flywheel-style runbooks document publishing flows.
- **Security delta:** Commit 1315e69 tightened the README roster notes without touching runtime
  scripts, keeping visibility high while leaving privileged workflows unchanged.
- **Watchlist:** Continue auditing workflow secrets and the expanding `scripts/` helpers that publish
  content bundles.

## Checklist

- [ ] Publish a data catalog describing available pipelines, schedules, and retention policies.
- [ ] Document onboarding instructions for new episode workspaces, including secret handling.
- [ ] Automate regression dashboards to flag drift across dependent repositories.
