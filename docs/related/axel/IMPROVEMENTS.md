# Suggested Improvements for Axel

This document aggregates recommended enhancements for the [axel](https://github.com/futuroptimist/axel) repository as discussed in previous analyses.

## Checklist

- [ ] Document `.gitignore` verification for `local/` directories and confirm `AXEL_REPO_FILE` points to an ignored path.
- [ ] Provide guidance on rotating the `DISCORD_BOT_TOKEN` and limiting bot permissions.
- [ ] Add a comprehensive `THREAT_MODEL.md` (see this directory) describing risks from cross-repo integrations and token handling.
- [ ] Offer optional encryption or cleanup guidance for `local/discord/` message logs.
- [ ] Review permissions for integrated tools such as `token.place` and `gabriel`.

These items can be tracked alongside other project milestones to reduce the chance of leaking sensitive data or expanding the attack surface unintentionally.
