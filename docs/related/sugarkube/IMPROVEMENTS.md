# Suggested Improvements for sugarkube

This document highlights improvement ideas for the
[futuroptimist/sugarkube](https://github.com/futuroptimist/sugarkube) repository.

## Current Snapshot (2025-10-08)

- **Status:** ✅ Roster confirmed on 2025-10-08 with PR #1192.
- **Stack:** Python automation, shell provisioning scripts, KiCad assets, Markdown docs, pytest/BATS
  suites, and CLI entry points.
- **Conventions:** Prompt docs under `docs/prompts/codex/`, README clarified for `python -m` usage,
  and tests now guard documentation instructions.
- **Security delta:** README guidance update plus doc-tests ensure CLI invocation stays accurate;
  coverage settings and workflows reorganized to highlight doc validation.
- **Watchlist:** Continue monitoring Raspberry Pi image scripts for credential usage and ensure new
  doc tests do not accidentally expose environment variables.

## Improvement Themes

- [ ] Publish explicit threat boundaries for the pi image builder scripts (cloud vs. local runs).
- [ ] Document procedures for revoking access if the `workflow_artifact_notifier` bot token leaks.
- [ ] Ensure Cloudflare tunnel templates ship with least-privilege credentials and rotate guidance.
