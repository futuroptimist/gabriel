# Suggested Improvements for DSPACE

This document tracks enhancement ideas for the
[democratizedspace/dspace](https://github.com/democratizedspace/dspace/tree/v3) repository.

## Current Snapshot (2025-10-08)

- **Status:** ✅ Roster confirmed on 2025-10-08 with the v3 branch shipping the achievements
  milestone (PR #1937).
- **Stack:** pnpm-managed workspace mixing Astro docs, Svelte quest UIs, and Node/TypeScript
  utilities, plus supporting Playwright/Jest suites and Netlify deploy tooling.
- **Conventions:** Accessibility docs stay under `docs/`, quest JSON under
  `frontend/src/pages/quests/`, and automated tests cover quest validation, achievements, and
  import/export flows.
- **Security delta:** Achievements release adds new quest metadata, Docker packaging, and CI jobs; a
  refreshed badge pipeline keeps Codecov, docs, and lint workflows active.
- **Watchlist:** Monitor bundle size growth from added art assets and keep pnpm overrides current so
  `canvas`/`@swc/core` native builds do not lag on security patches.

## Improvement Themes

- [ ] Document content signing or checksum workflows so community quest bundles are tamper evident.
- [ ] Expand automated checks that ensure newly added assets stay within privacy and licensing
      guidelines.
- [ ] Review quest telemetry collectors whenever new tutorials or offline flows are introduced.
