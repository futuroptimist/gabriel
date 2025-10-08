# Suggested Improvements for gitshelves

This document highlights possible enhancements for
[futuroptimist/gitshelves](https://github.com/futuroptimist/gitshelves).

## Current Snapshot (2025-10-08)

- **Status:** ✅ Roster entry reconfirmed via PR #144 on 2025-10-07.
- **Stack:** Python CLI + OpenSCAD templates, STL viewer assets, pytest, and GitHub Actions for lint
  and tests.
- **Conventions:** Prompt docs stay in `docs/prompts/codex/`; baseplate templates now selectable from
  CLI/SCAD flows; workflows split by `01-`/`02-` naming convention.
- **Security delta:** New baseplate selector surfaces additional template inputs—validate user-supplied
  names and guard new CLI flags.
- **Watchlist:** Keep STL preview pipeline in CI to flag tampered templates and ensure CLI sanitizes
  template names before hitting OpenSCAD.

## Improvement Themes

- [ ] Document how to validate STL checksums before printing block sets.
- [ ] Provide guidance on distributing viewer builds without exposing GitHub API tokens.
- [ ] Consider adding a sandbox mode for rendering contributions before merging.
