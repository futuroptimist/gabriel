# Suggested Improvements for pr-reaper

This document tracks recommendations for the
[futuroptimist/pr-reaper](https://github.com/futuroptimist/pr-reaper) repository.

## Current Snapshot (2025-10-08)

- **Status:** ✅ Roster reconfirmed after PR #34 merged on 2025-10-06.
- **Stack:** Node.js CLI plus GitHub Actions (`ci.yml`, `close-my-open-prs.yml`) orchestrated with pnpm
  and Shell scripts.
- **Conventions:** Prompt docs under `docs/prompts/codex/`; repo now includes editorconfig, PR
  template, and expanded workflow automation.
- **Security delta:** PR #34 fixed workflow syntax and shipped an explicit bulk-closure workflow—review
  concurrency safeguards and dry-run toggles.
- **Watchlist:** Confirm GitHub Actions tokens operate with least privilege and the new workflow
  surfaces environment variables carefully in logs.

## Improvement Themes

- [ ] Document how to run the `close-my-open-prs` workflow safely against forks.
- [ ] Provide rate-limit guidance when sweeping large PR backlogs.
- [ ] Add integration tests that simulate dry-run vs. destructive modes.
