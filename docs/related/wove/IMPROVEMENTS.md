# Suggested Improvements for wove

This document tracks opportunities for the
[futuroptimist/wove](https://github.com/futuroptimist/wove) repository.

## Current Snapshot (2025-09-29)

- **Status:** ✅ via the Futuroptimist roster.
- **Stack:** Python utilities, OpenSCAD models, Sphinx docs, and pytest.
- **Conventions:** Prompt docs live under `docs/prompts/codex/`, hardware CAD assets pair with STL
  exports, and CI covers lint/tests/docs.
- **Security delta:** PR #105 added full repository overview docs, codified workflows, and new STL
  assets. No networked services were introduced, but contributors should vet large STL additions.
- **Watchlist:** Monitor `dict/allow.txt` growth and ensure the viewer pipeline remains reproducible.

## Improvement Themes

- [ ] Add a signed checksum list for published STL files.
- [ ] Document safe disposal for scrap filament and electronics from the knitting machine builds.
- [ ] Provide an architecture diagram showing how scripts assemble CAD artifacts.
