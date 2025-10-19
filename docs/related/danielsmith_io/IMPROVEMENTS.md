# Suggested Improvements for danielsmith.io

This document tracks enhancement ideas for the
[futuroptimist/danielsmith.io](https://github.com/futuroptimist/danielsmith.io) repository.

## Current Snapshot (2025-10-18)

- **Status:** ✅ (roster snapshot 2025-10-18 23:02 UTC).
- **Stack:** Vite + Three.js portfolio scene with TypeScript and GLSL assets.
- **Conventions:** Screenshots and assets live in `public/`, prompts under `docs/prompts/codex/`, and
  CI mirrors flywheel's lint/test/docs split.
- **Security delta:** Commit 2f1e29e refreshed the launch screenshot only; runtime code and build
  tooling remain unchanged.
- **Watchlist:** Continue checking Three.js version pins and ensure screenshot updates do not mask UI
  regressions.

## Improvement Backlog

- [ ] Document deployment hardening tips (headers, CSP) for the static site.
- [ ] Provide guidance on privacy-sensitive assets embedded in the portfolio.
- [ ] Add uptime monitoring instructions for the static hosting provider.
