# Suggested Improvements for DSPACE

This document tracks enhancement ideas for the
[democratizedspace/dspace](https://github.com/democratizedspace/dspace/tree/v3) repository.

## Current Snapshot (2025-10-18)

- **Status:** ✅ per the Futuroptimist roster (v3 branch snapshot at 2025-10-18 23:02 UTC).
- **Stack:** pnpm-managed monorepo with an Astro/Svelte front-end, supporting TypeScript tooling, and
  Python helpers for quest data ingestion.
- **Conventions:** Uses `outages/` to log CI incidents, `scripts/` benchmarks to guard quest data, and
  Vitest/Jest suites alongside Python tests.
- **Security delta:** No code landed since the 2025-09-29 snapshot; the repository remains stable while
  monitoring pipelines for quest uploads.
- **Watchlist:** Asset bloat and CDN quotas, telemetry scrubbing for new quests, and making sure the
  absent `v3` branch reference is documented for contributors cloning via README instructions.

## Improvement Themes

- [ ] Document content signing or checksum workflows so community quest bundles are tamper evident.
- [ ] Expand automated checks that ensure newly added assets stay within privacy and licensing
      guidelines.
- [ ] Review quest telemetry collectors whenever new tutorials or offline flows are introduced.
