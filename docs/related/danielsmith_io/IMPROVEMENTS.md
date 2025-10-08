# Suggested Improvements for danielsmith.io

This document summarizes follow-ups for the
[futuroptimist/danielsmith.io](https://github.com/futuroptimist/danielsmith.io) repository.

## Current Snapshot (2025-10-08)

- **Status:** ✅ Roster reconfirmed after PR #111 landed on 2025-10-07.
- **Stack:** Vite + Three.js scene rendered with TypeScript, Vitest/Playwright tests, and npm scripts.
- **Conventions:** Prompt docs remain under `docs/prompts/codex/`; HUD focus announcements now live in
  `src/lib/a11y.ts`; CI retains screenshot capture flows.
- **Security delta:** Added live-region HUD cues require inspecting DOM updates to avoid leaking hidden
  debug text or exposing focus loops.
- **Watchlist:** Ensure accessibility helpers strip developer-only logging before deployment and review
  Playwright recordings for inadvertent PII.

## Improvement Themes

- [ ] Document how to rotate assets in `docs/resume` without leaking personal data.
- [ ] Provide a hardening guide for hosting the Vite build on static providers.
- [ ] Add instructions for purging cached screenshots if credentials appear.
