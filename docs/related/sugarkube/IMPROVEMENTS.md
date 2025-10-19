# Suggested Improvements for sugarkube

This document highlights open improvements for the
[futuroptimist/sugarkube](https://github.com/futuroptimist/sugarkube) repository.

## Current Snapshot (2025-10-18)

- **Status:** ❌ (roster snapshot 2025-10-18 23:02 UTC shows the latest CI run failed or was cancelled).
- **Stack:** Python tooling, KiCad hardware assets, Raspberry Pi imaging scripts, and extensive GitHub
  Actions workflows (pi image builds, SCAD exports, spellcheck, docs).
- **Conventions:** Prompt docs in `docs/prompts/codex/`, Taskfile/Justfile automation for hardware
  builds, and tests spanning shell scripts, Python modules, and OpenSCAD renders.
- **Security delta:** PR #1348 added a long-term vision doc plus new workflows and scripts supporting
  Pi image builds and telemetry, broadening CI surfaces and artifact handling.
- **Watchlist:** Investigate the failing workflow, audit new telemetry scripts
  (`scripts/workflow_artifact_notifier.py`, `scripts/token_place_replay_samples.py`), and ensure QR code
  assets do not leak operational secrets.

## Improvement Themes

- [ ] Restore CI health before layering new features; document root cause of the failing workflow.
- [ ] Harden Pi imaging scripts against credential leakage (especially when bundling token.place
      samples).
- [ ] Publish signed manifests for STL and Pi image artifacts.
