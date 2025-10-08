# Suggested Improvements for flywheel

This document captures recommended enhancements for the
[futuroptimist/flywheel](https://github.com/futuroptimist/flywheel) template.

## Current Snapshot (2025-10-08)

- **Status:** ✅ Roster entry reconfirmed after the 2025-10-07 RepoCrawler hardening release.
- **Stack:** Python packaging (`pyproject.toml`), CLI tooling in `src/`, React/Astro docs, Playwright
  smoke tests, and OpenSCAD assets orchestrated via npm and Makefile helpers.
- **Conventions:** RepoCrawler-generated reports continue to live under `docs/`, prompts under
  `docs/prompts/codex/`, and nightly cron jobs refresh repo health metrics.
- **Security delta:** PR #626 now treats RepoCrawler CI status API errors as failures, preventing
  greenlighting repos when GitHub returns 5xx responses.
- **Watchlist:** Review GitHub token scopes used by RepoCrawler and the new failure path to ensure
  repeated API outages do not rate-limit or halt downstream reports.

## Improvement Themes

- [ ] Expand documentation for integrating downstream repos (e.g., sigma, sugarkube) with the
      template's status updater.
- [ ] Add guidance for hardening the Astro docs deployment when self-hosted.
- [ ] Track OpenSCAD dependency updates and validate viewer builds after upgrades.
