# Suggested Improvements for gitshelves

This document summarizes enhancement opportunities for the
[futuroptimist/gitshelves](https://github.com/futuroptimist/gitshelves) repository.

## Current Snapshot (2025-10-18)

- **Status:** ✅ (roster snapshot 2025-10-18 23:02 UTC).
- **Stack:** Python 3.11 package bundling OpenSCAD generators, Typer CLI wrappers, and pytest snapshot
  coverage for SCAD outputs.
- **Conventions:** Prompt docs consolidated under `docs/prompts/codex/`, SCAD sources in `openscad/`
  plus Python wrappers in `gitshelves/`, and tests verify CLI ergonomics alongside geometry snapshots.
- **Security delta:** PR #186 added SCAD snapshot tests, CLI scaffolding, and new docs—improving
  reproducibility but increasing dependency surface (Typer, GitHub APIs) that must be monitored.
- **Watchlist:** Review GitHub token usage in `gitshelves/core/github.py`, ensure generated SCAD files
  stay deterministic, and keep CLI environment variables masked in docs.

## Improvement Backlog

- [ ] Provide checksum manifests for exported STL files.
- [ ] Document how to rotate GitHub tokens used for fetching contribution data.
- [ ] Offer optional anonymization when rendering public contribution histories.
