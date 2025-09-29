# Suggested Improvements for gitshelves

This document highlights possible enhancements for
[futuroptimist/gitshelves](https://github.com/futuroptimist/gitshelves).

## Current Snapshot (2025-09-29)

- **Status:** ✅ in the Futuroptimist roster.
- **Stack:** Python CLI with OpenSCAD/SCAD templates, pytest suites, and npm-based viewer assets.
- **Conventions:** Prompt docs relocated to `docs/prompts/codex/`, viewer HTML lives under `docs/`,
  and `gitshelves/scad.py` renders STL output.
- **Security delta:** Prompt doc move plus refreshed CLI/tests (PR #109) expanded automation but did
  not modify STL generation logic.
- **Watchlist:** Ensure `dict/allow.txt` stays aligned with new SCAD terminology and keep SCAD
  renders in CI to detect tampering.

## Improvement Themes

- [ ] Document how to validate STL checksums before printing block sets.
- [ ] Provide guidance on distributing viewer builds without exposing GitHub API tokens.
- [ ] Consider adding a sandbox mode for rendering contributions before merging.
