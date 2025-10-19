# Suggested Improvements for sigma

This document tracks enhancement ideas for the
[futuroptimist/sigma](https://github.com/futuroptimist/sigma) project.

## Current Snapshot (2025-10-18)

- **Status:** ✅ (roster snapshot 2025-10-18 23:02 UTC).
- **Stack:** ESP32 firmware with PlatformIO, Python orchestration, and a new Three.js viewer alongside
  Python audio/TTS/Whisper clients.
- **Conventions:** Prompt docs live under `docs/prompts/codex/`, hardware assets in `hardware/` and
  `docs/hardware/`, and sigma-specific scripts ship in `scripts/` with Playwright tests for the viewer.
- **Security delta:** PR #173 introduced configurable Whisper endpoints (`SIGMA_WHISPER_URL`), expanded
  docs, and bundled large Three.js artifacts, raising supply-chain risk but clarifying operations.
- **Watchlist:** Track vendor JS hashes, ensure firmware secrets remain isolated, and test Whisper URL
  overrides for SSRF or downgrade pitfalls.

## Improvement Backlog

- [ ] Document secure provisioning for local Whisper servers used during overrides.
- [ ] Add guidance for signing firmware images and distributing checksum manifests.
- [ ] Expand Playwright coverage to include authenticated viewer flows once available.
