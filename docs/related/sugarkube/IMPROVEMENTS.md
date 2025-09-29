# Suggested Improvements for sugarkube

This document highlights improvement ideas for the
[futuroptimist/sugarkube](https://github.com/futuroptimist/sugarkube) repository.

## Current Snapshot (2025-09-29)

- **Status:** ✅ per the Futuroptimist roster.
- **Stack:** Python automation, shell scripts, KiCad assets, docs with Markdown and HTML, and
  extensive pytest/BATS suites.
- **Conventions:** Prompt docs live under `docs/prompts/codex/`, outages catalog incidents, and
  `scripts/` host provisioning helpers for Raspberry Pi clusters.
- **Security delta:** PR #1148 shipped the `start_here` CLI helper, new CI workflows (pi-image,
  spellcheck, SCAD to STL), and detailed docs for pi image building—expanding attack surface if
  secrets leak during automation.
- **Watchlist:** Keep scanning the new `docs/images/qr/` assets for embedded secrets and verify that
  telemetry scripts respect opt-in defaults.

## Improvement Themes

- [ ] Publish explicit threat boundaries for the pi image builder scripts (cloud vs. local runs).
- [ ] Document procedures for revoking access if the `workflow_artifact_notifier` bot token leaks.
- [ ] Ensure Cloudflare tunnel templates ship with least-privilege credentials and rotate guidance.
