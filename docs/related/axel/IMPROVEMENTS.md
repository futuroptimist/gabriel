# Suggested Improvements for Axel

This document aggregates recommended enhancements for the
[axel](https://github.com/futuroptimist/axel) repository as discussed in previous analyses.

## Current Snapshot (2025-10-08)

- **Status:** ✅ Confirmed on 2025-10-08 as PR #159 shipped Discord summary formatting tweaks.
- **Stack:** Python 3.11 automation, Discord bot integrations, OpenSCAD artifacts, and hillclimb
  cards under `.axel/`.
- **Conventions:** Prompts remain in `docs/prompts/codex/`; bullet summaries now render in Discord
  updates; tests exercise CLI repo scans.
- **Security delta:** Discord summary change introduces new Markdown parsing of remote output—verify
  escaping to avoid injection.
- **Watchlist:** Audit hillclimb cards that fetch remote metadata and confirm Discord webhooks mask
  tokens when bullet-mode is enabled.

## Checklist

- [ ] Document `.gitignore` verification for `local/` directories and confirm `AXEL_REPO_FILE` points
      to an ignored path.
- [ ] Provide guidance on rotating the `DISCORD_BOT_TOKEN` and limiting bot permissions.
- [ ] Add a comprehensive `THREAT_MODEL.md` (see this directory) describing risks from cross-repo
      integrations and token handling.
- [ ] Offer optional encryption or cleanup guidance for `local/discord/` message logs.
- [ ] Review permissions for integrated tools such as `token.place` and `gabriel`.
