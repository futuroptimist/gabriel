# Suggested Improvements for f2clipboard

This document captures follow-up opportunities for the
[futuroptimist/f2clipboard](https://github.com/futuroptimist/f2clipboard) project.

## Current Snapshot (2025-10-08)

- **Status:** ✅ Roster reconfirmed after the 2025-10-06 automation update (PR #158).
- **Stack:** Python 3 CLI packaged via `pyproject.toml`, GitHub Action entrypoint, pytest + VCR
  suites, and optional Slack/Jira plugins.
- **Conventions:** Prompt docs in `docs/prompts/codex/`, environment templates in `.env.example`, and
  scripts orchestrated via `scripts/checks.sh` and pre-commit.
- **Security delta:** PR #158 introduced automatic merge-patch application, requiring cautious review
  of repo-local patch files and CI permissions.
- **Watchlist:** Ensure the new automation cannot apply untrusted patches from issue content and that
  cached transcripts in `~/.f2clipboard` still redact tokens promptly.

## Improvement Themes

- [ ] Document best practices for storing GitHub tokens referenced by the CLI and GitHub Action.
- [ ] Expand integration tests covering the optional Jira plugin across failure cases.
- [ ] Publish a security note describing how to rotate cached task data in `~/.f2clipboard`.
