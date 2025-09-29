# Suggested Improvements for flywheel

This document captures recommended enhancements for the
[futuroptimist/flywheel](https://github.com/futuroptimist/flywheel) template.

## Current Snapshot (2025-09-29)

- **Status:** ✅ via the Futuroptimist roster refresh.
- **Stack:** Python packaging (`pyproject.toml`), Node/Playwright tooling, OpenSCAD assets, and a
  docs-site built with Astro/React, all managed via npm and Makefile helpers.
- **Conventions:** Maintains prompt libraries in `docs/prompts/codex/`, runs nightly repo scans,
  and publishes STL/GLB assets for the viewer.
- **Security delta:** Automated status workflow updated README to match the new roster sync; no
  runtime code changes beyond documentation.
- **Watchlist:** Ensure the repo-status automation keeps secrets minimal and continue reviewing
  generated STL artifacts before publishing.

## Improvement Themes

- [ ] Expand documentation for integrating downstream repos (e.g., sigma, sugarkube) with the
      template's status updater.
- [ ] Add guidance for hardening the Astro docs deployment when self-hosted.
- [ ] Track OpenSCAD dependency updates and validate viewer builds after upgrades.
