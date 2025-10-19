# Suggested Improvements for f2clipboard

This document captures proposed enhancements for the
[futuroptimist/f2clipboard](https://github.com/futuroptimist/f2clipboard) project.

## Current Snapshot (2025-10-18)

- **Status:** ✅ (roster synced 2025-10-18 23:02 UTC).
- **Stack:** Python 3.11 CLI packaged with `pyproject.toml`, rich unit tests, and GitHub Action
  scaffolding; new Markdown automation plans accompany the CLI.
- **Conventions:** Prompt docs live under `docs/prompts/codex/`, merge helpers moved into
  `f2clipboard/merge_*`, and cassette fixtures guard Codex task scraping behavior.
- **Security delta:** PR #162 rebuilt the CLI, introducing plugin scaffolding, secret helpers, and
  markdown polish plans; the new `.env.example` clarifies credential usage but increases the number of
  places API tokens may live locally.
- **Watchlist:** Harden plugin loading paths, continue scanning cached Codex transcripts, and document
  rotation guidance for secrets stored in `~/.f2clipboard`.

## Checklist

- [ ] Publish a security note describing how to rotate cached task data in `~/.f2clipboard`.
- [ ] Document `f2clipboard secret` lifecycle guidance and encourage low-privilege tokens.
- [ ] Add a dry-run mode for the GitHub Action so maintainers can rehearse new filters safely.
