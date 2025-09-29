# Suggested Improvements for f2clipboard

This document captures follow-up opportunities for the
[futuroptimist/f2clipboard](https://github.com/futuroptimist/f2clipboard) project.

## Current Snapshot (2025-09-29)

- **Status:** ✅ in the Futuroptimist roster.
- **Stack:** Python 3 CLI packaged with `pyproject.toml`, optional GitHub Action (`action.yml`), and
  pytest suites with VCR cassettes.
- **Conventions:** Prompt docs moved under `docs/prompts/codex/`; scripts run via `scripts/checks.sh`
  and `pre-commit` handles formatting.
- **Security delta:** PR #143 introduced full CLI modules, secret handling helpers, and prompt docs
  relocation. New `secret.py` and plugin loaders warrant review of credential storage practices.
- **Watchlist:** Verify `.env` guidance stays current and that cached Codex transcripts purge secrets
  after use.

## Improvement Themes

- [ ] Document best practices for storing GitHub tokens referenced by the CLI and GitHub Action.
- [ ] Expand integration tests covering the optional Jira plugin across failure cases.
- [ ] Publish a security note describing how to rotate cached task data in `~/.f2clipboard`.
