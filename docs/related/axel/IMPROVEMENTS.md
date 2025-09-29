# Suggested Improvements for Axel

This document aggregates recommended enhancements for the
[axel](https://github.com/futuroptimist/axel) repository as discussed in previous analyses.

## Current Snapshot (2025-09-29)

- **Status:** ✅ (per the Futuroptimist roster).
- **Stack:** Python 3.11 app with Discord bot helpers, OpenSCAD hardware models, and Makefile tasks.
- **Conventions:** Prompt docs consolidated under `docs/prompts/codex/`, hillclimb automations live
  in `.axel/`, and tests cover repo management plus Discord bot stubs.
- **Security delta:** PR #131 relocated prompt docs and refreshed hillclimb scaffolding, reinforcing
  the habit of keeping automation scripts under version control.
- **Watchlist:** Continue auditing local `repos.txt` usage and ensure hillclimb scripts never commit
  tokens.

## Checklist

- [ ] Document `.gitignore` verification for `local/` directories and confirm `AXEL_REPO_FILE` points
      to an ignored path.
- [ ] Provide guidance on rotating the `DISCORD_BOT_TOKEN` and limiting bot permissions.
- [ ] Add a comprehensive `THREAT_MODEL.md` (see this directory) describing risks from cross-repo
      integrations and token handling.
- [ ] Offer optional encryption or cleanup guidance for `local/discord/` message logs.
- [ ] Review permissions for integrated tools such as `token.place` and `gabriel`.
