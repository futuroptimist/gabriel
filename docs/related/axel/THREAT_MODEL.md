# Axel Threat Model

The **axel** repository organizes collections of repositories and runs a local Discord bot for capturing messages.
This document outlines assumed threats and mitigations when using axel.

## Security Assumptions

- Axel runs on hardware controlled by the user.
- Discord bot tokens and repository lists are stored locally and kept out of source control.
- Users may integrate axel with other projects such as `gabriel` or `token.place`.

## Attack Surface

- **Repository leak** – `repos.txt` may expose private repository URLs if accidentally committed.
- **Bot impersonation** – Leaked `DISCORD_BOT_TOKEN` allows attackers to control the bot and read captured messages.
- **Cross‑repo integrations** – Future features connecting axel with other tools expand the attack surface and could leak data across repos.
- **Data accumulation** – Message logs in `local/discord/` may store sensitive information over time.

## Mitigations

- Keep private repository lists in a `local/` directory ignored via `.gitignore`.
- Use environment variables for tokens and rotate them periodically.
- Limit bot permissions to only what is necessary for message ingestion.
- Consider optional encryption or regular cleanup of the `local/discord/` directory.
- Document a checklist for verifying `.gitignore` entries and reviewing token usage.
