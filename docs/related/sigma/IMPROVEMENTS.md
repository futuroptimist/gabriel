# Suggested Improvements for sigma

This document summarizes enhancements for the
[futuroptimist/sigma](https://github.com/futuroptimist/sigma) repository.

## Current Snapshot (2025-09-29)

- **Status:** ✅ on the Futuroptimist roster.
- **Stack:** Python utilities, OpenSCAD CAD models, and Makefile automation complemented by
  TypeScript prompt docs.
- **Conventions:** Prompt documents now live under `docs/prompts/codex/`, with SCAD builds handled by
  `scripts/build_stl.sh` and tests covering clamp math and utility functions.
- **Security delta:** PR #95 reorganized prompt docs and added hardware documentation; no new
  firmware or OTA channels were introduced.
- **Watchlist:** Continue validating the STL outputs and ensuring `llms.py` remains offline friendly.

## Improvement Themes

- [ ] Publish an end-to-end assembly hardening checklist for the Sigma S1 enclosure.
- [ ] Add examples for rotating encryption keys if Sigma integrates with `token.place` in the future.
- [ ] Document how to audit generated STL hashes prior to printing.
