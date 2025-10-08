# Suggested Improvements for sigma

This document summarizes enhancements for the
[futuroptimist/sigma](https://github.com/futuroptimist/sigma) repository.

## Current Snapshot (2025-10-08)

- **Status:** ✅ Roster refreshed after PR #131 landed on 2025-10-07.
- **Stack:** Python utilities controlling ESP32 firmware flows, OpenSCAD models, tests, and prompts
  housed in `docs/prompts/codex/`.
- **Conventions:** GitHub Actions lint/test workflows split into `01-` and `02-` pipelines; nested LLM
  segment parsing now normalized in source tests.
- **Security delta:** PR #131 improved parsing of nested LLM text segments and hardened GitHub
  workflows—verify logs for token leaks during new parsing paths.
- **Watchlist:** Monitor firmware build artifacts for size creep and ensure nested-segment handling
  cannot be coerced into executing markup sent from untrusted Bluetooth clients.

## Improvement Themes

- [ ] Publish an end-to-end assembly hardening checklist for the Sigma S1 enclosure.
- [ ] Add examples for rotating encryption keys if Sigma integrates with `token.place` in the future.
- [ ] Document how to audit generated STL hashes prior to printing.
