# Suggested Improvements for wove

This document tracks opportunities for the
[futuroptimist/wove](https://github.com/futuroptimist/wove) repository.

## Current Snapshot (2025-10-08)

- **Status:** ✅ Confirmed on 2025-10-08 after the crochet translation CLI landed (PR #126).
- **Stack:** Python utilities, crochet pattern translation CLI, STL/CAD assets, Sphinx docs, and
  pytest coverage.
- **Conventions:** Prompt docs remain under `docs/prompts/codex/`; new CLI surfaces live in
  `wove/cli.py` with tests covering translation mappings; CI orchestrated via `01-`/`02-` workflows.
- **Security delta:** CLI introduces pattern parsing of untrusted input—ensure regexes and lookups
  handle malformed patterns safely.
- **Watchlist:** Keep translation dictionaries sanitized and review new CLI dependencies for license
  compatibility.

## Improvement Themes

- [ ] Add a signed checksum list for published STL files.
- [ ] Document safe disposal for scrap filament and electronics from the knitting machine builds.
- [ ] Provide an architecture diagram showing how scripts assemble CAD artifacts.
