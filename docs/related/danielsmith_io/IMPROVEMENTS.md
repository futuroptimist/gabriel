# Suggested Improvements for danielsmith.io

This document summarizes follow-ups for the
[futuroptimist/danielsmith.io](https://github.com/futuroptimist/danielsmith.io) repository.

## Current Snapshot (2025-09-29)

- **Status:** ✅ in the Futuroptimist roster.
- **Stack:** Vite + Three.js site with TypeScript, Playwright/Vitest tests, and npm-managed
  workflows.
- **Conventions:** Prompt docs live under `docs/prompts/codex/`, scripts generate floorplan diagrams,
  and CI captures launch screenshots.
- **Security delta:** Latest commit refreshed the launch screenshot workflow and kept automation in
  place; no new backend components were added.
- **Watchlist:** Monitor Playwright artifacts for PII and ensure resume assets stay current.

## Improvement Themes

- [ ] Document how to rotate assets in `docs/resume` without leaking personal data.
- [ ] Provide a hardening guide for hosting the Vite build on static providers.
- [ ] Add instructions for purging cached screenshots if credentials appear.
