# Suggested Improvements for futuroptimist

This document aggregates enhancement ideas for the
[futuroptimist/futuroptimist](https://github.com/futuroptimist/futuroptimist) repository.

## Current Snapshot (2025-10-08)

- **Status:** ✅ Roster automation ran 2025-10-08 via update-repo-status workflow.
- **Stack:** Python utilities managed with `uv`, Markdown docs, GitHub Actions for lint/tests/docs, and
  the new `update-repo-status.yml` scheduler.
- **Conventions:** Prompts under `docs/prompts/codex/`, incidents in `outages/`, with 01/02/03 workflow
  naming mirroring flywheel.
- **Security delta:** New CI suites (lint/tests/docs) plus status updater workflow landed in PR
  `docs: update repo statuses`, increasing reliance on PAT/OIDC config.
- **Watchlist:** Keep workflow tokens scoped minimally and ensure the status updater handles rate-limit
  failures gracefully.

## Checklist

- [ ] Publish a data catalog describing available pipelines, schedules, and retention policies.
- [ ] Document onboarding instructions for new episode workspaces, including secret handling.
- [ ] Automate regression dashboards to flag drift across dependent repositories.
