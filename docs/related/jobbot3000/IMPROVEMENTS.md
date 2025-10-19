# Suggested Improvements for jobbot3000

This document summarizes improvements for the
[futuroptimist/jobbot3000](https://github.com/futuroptimist/jobbot3000) repository.

## Current Snapshot (2025-10-18)

- **Status:** ✅ (roster snapshot 2025-10-18 23:02 UTC).
- **Stack:** Node 20 monorepo with CLI automation, web UI, playwright/Vitest tests, and Docker
deployments.
- **Conventions:** Prompt docs under `docs/prompts/codex/`, screenshots in `docs/screenshots/`, and
  automation scripts under `scripts/`.
- **Security delta:** PR #835 enabled the native CLI inside docker-compose deployments, added thousands
  of lines of documentation and tests, and expanded script coverage—significantly widening the surface
  of long-running Node services.
- **Watchlist:** Audit `.env.example` defaults, ensure docker-compose CLI commands respect least
  privilege, and monitor new analytics modules for data retention.

## Improvement Themes

- [ ] Document token rotation for listings provider integrations.
- [ ] Publish guidance on securing the new web server endpoints introduced by the CLI enablement.
- [ ] Add automated checks that fail builds if analytics exports leak PII.
