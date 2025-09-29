# Suggested Improvements for pr-reaper

This document tracks recommendations for the
[futuroptimist/pr-reaper](https://github.com/futuroptimist/pr-reaper) repository.

## Current Snapshot (2025-09-29)

- **Status:** ✅ on the Futuroptimist roster.
- **Stack:** Node.js CLI (pnpm/npm) with GitHub Action automation and lightweight TypeScript-free
  scripts.
- **Conventions:** Prompts relocated to `docs/prompts/codex/`, workflows manage PR cleanup and CI,
  and `scripts/scan-secrets.py` is bundled for local validation.
- **Security delta:** PR #20 added status badges, a `close-my-open-prs` workflow, and standard repo
  scaffolding; new workflows introduce GitHub token usage that must remain scoped.
- **Watchlist:** Audit workflow permissions and ensure automation uses dry-run mode by default.

## Improvement Themes

- [ ] Document how to run the `close-my-open-prs` workflow safely against forks.
- [ ] Provide rate-limit guidance when sweeping large PR backlogs.
- [ ] Add integration tests that simulate dry-run vs. destructive modes.
