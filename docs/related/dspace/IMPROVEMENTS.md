# Suggested Improvements for DSPACE

This document tracks enhancement ideas for the
[democratizedspace/dspace](https://github.com/democratizedspace/dspace/tree/v3) repository.

## Current Snapshot (2025-09-29)

- **Status:** ✅ per the Futuroptimist roster (v3 branch).
- **Stack:** pnpm-managed monorepo with a Svelte/TypeScript frontend, Python tooling, and Ansible
  automation for quest publishing.
- **Conventions:** Uses `outages/` to log CI incidents, `scripts/` benchmarks to guard quest data,
  and Vitest/Jest/Vitest-style suites alongside Python tests.
- **Security delta:** PR #1906 landed large batches of new quest assets and outage entries while
  extending regression tests for quest validation and metrics; no infrastructure changes.
- **Watchlist:** Keep an eye on the asset bloat and ensure CDN or storage buckets enforce size
  limits; confirm new quests receive the expected telemetry sanitisation.

## Improvement Themes

- [ ] Document content signing or checksum workflows so community quest bundles are tamper evident.
- [ ] Expand automated checks that ensure newly added assets stay within privacy and licensing
      guidelines.
- [ ] Review quest telemetry collectors whenever new tutorials or offline flows are introduced.
