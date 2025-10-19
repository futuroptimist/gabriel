# Suggested Improvements for Axel

This document aggregates recommended enhancements for the
[axel](https://github.com/futuroptimist/axel) repository as discussed in previous analyses.

## Current Snapshot (2025-10-18)

- **Status:** ✅ (per the Futuroptimist roster).
- **Stack:** Python 3.11 automation suite with Discord bot helpers, hillclimb automation under
  `.axel/`, and JSON-friendly CLI outputs.
- **Conventions:** Prompt docs consolidated under `docs/prompts/codex/`, hillclimb automations live in
  `.axel/`, and tests cover repo management, Discord bots, and CLI pipelines.
- **Security delta:** PR #210 delivered JSON output support and a major repo expansion (Discord bot,
  token.place integrations, policy docs), increasing secret touchpoints and automation surfaces.
- **Watchlist:** Audit `.env.example` guidance, confirm hillclimb scripts never commit tokens, and
  document how the new JSON output mode handles sensitive fields.

## Checklist

- [ ] Document `.gitignore` verification for `local/` directories and confirm `AXEL_REPO_FILE` points
      to an ignored path.
- [ ] Provide guidance on rotating the `DISCORD_BOT_TOKEN` and limiting bot permissions.
- [ ] Add a comprehensive `THREAT_MODEL.md` (see this directory) describing risks from cross-repo
      integrations and token handling.
- [ ] Offer optional encryption or cleanup guidance for `local/discord/` message logs.
- [ ] Review permissions for integrated tools such as `token.place` and `gabriel`.
