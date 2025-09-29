# Suggested Improvements for futuroptimist

This document aggregates enhancement ideas for the
[futuroptimist/futuroptimist](https://github.com/futuroptimist/futuroptimist) repository.

## Current Snapshot (2025-09-29)

- **Status:** ✅ (refreshed hourly via the README roster sync committed on 2025-09-29).
- **Stack:** Python 3.12+ utilities managed with `uv`, Markdown docs, and GitHub Actions
  workflows for linting, tests, docs, and coverage.
- **Conventions:** Keeps automation prompts under `docs/prompts/codex/`, records incidents in
  `outages/`, and mirrors flywheel-style runbooks.
- **Security delta:** README now advertises the automated roster check; no new code paths were
  introduced, but the monitoring workflow increases visibility into stale repos.
- **Watchlist:** Continue auditing workflow secrets and the expanding `scripts/` helpers that
  publish content bundles.

## Checklist

- [ ] Publish a data catalog describing available pipelines, schedules, and retention policies.
- [ ] Document onboarding instructions for new episode workspaces, including secret handling.
- [ ] Automate regression dashboards to flag drift across dependent repositories.
