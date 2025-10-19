# Suggested Improvements for pr-reaper

This document captures recommended enhancements for the
[futuroptimist/pr-reaper](https://github.com/futuroptimist/pr-reaper) repository.

## Current Snapshot (2025-10-18)

- **Status:** ✅ (roster snapshot 2025-10-18 23:02 UTC).
- **Stack:** TypeScript composite GitHub Action compiled to `dist/`, backed by vitest and Playwright
  tests, with automation prompts in `docs/prompts/codex/`.
- **Conventions:** Release artifacts live in `dist/`, prompts drive automation behavior, and CI mirrors
  consumer environments.
- **Security delta:** PR #51 updated the action to forward composite inputs to the runtime environment,
  expanded docs, and added workflow examples, reducing misconfiguration risk without altering scopes.
- **Watchlist:** Continue validating `dist/` outputs after TypeScript changes and ensure repository
  secrets remain masked when forwarding inputs.

## Improvement Themes

- [ ] Document environment variable expectations for self-hosted runners.
- [ ] Provide dry-run guardrails explaining which PRs will be closed before execution.
- [ ] Add dependency audit notes so consumers trust the published `dist/` bundle.
