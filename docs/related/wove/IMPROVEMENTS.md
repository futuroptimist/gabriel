# Suggested Improvements for wove

This document summarizes opportunities to improve the
[futuroptimist/wove](https://github.com/futuroptimist/wove) repository.

## Current Snapshot (2025-10-18)

- **Status:** ✅ (roster snapshot 2025-10-18 23:02 UTC).
- **Stack:** Python 3.11 package with Typer-based CLI tooling, OpenSCAD CAD assets, and Sphinx docs
  describing textile workflows.
- **Conventions:** Prompt docs under `docs/prompts/codex/`, CAD in `cad/` and `stl/`, and tests covering
  pattern visualization plus gauge math.
- **Security delta:** PR #158 added the pattern visualization harness, schema docs, and large STL
  assets, expanding CLI surfaces and requiring careful handling of pattern data.
- **Watchlist:** Validate pattern JSON imports, keep the visualization CLI from reading arbitrary
  files, and publish checksums for the new STL assets.

## Improvement Themes

- [ ] Document secure workflows for sharing pattern JSON files.
- [ ] Add guidance for verifying STL checksums before printing.
- [ ] Provide threat notes on safeguarding the visualization CLI from untrusted patterns.
