# Suggested Improvements for flywheel

This document aggregates suggested enhancements for the
[futuroptimist/flywheel](https://github.com/futuroptimist/flywheel) repository.

## Current Snapshot (2025-10-18)

- **Status:** ✅ per the Futuroptimist roster (2025-10-18 23:02 UTC).
- **Stack:** Polyglot template bundling Python tooling, TypeScript viewer code, and CAD assets with
  Makefiles and GitHub Actions mirroring Gabriel's CI surface.
- **Conventions:** Prompt docs under `docs/prompts/codex/`, incident tracking via `outages/`, and
  repo feature summaries that seed downstream templates.
- **Security delta:** Commit 86f4f03 updated the repo feature summary to reflect the latest automations
  without altering the build pipelines, so security posture is unchanged but documentation is current.
- **Watchlist:** Ensure template secrets referenced in `infra/` scripts stay rotated and that bundled
  CAD exports continue to ship with checksums.

## Improvement Backlog

- [ ] Expand documentation around secret provisioning for template-driven repos.
- [ ] Provide a quick-start for porting existing projects into the flywheel scaffolding.
- [ ] Add automated checks verifying CAD assets render with known-good parameters.
