# f2clipboard Threat Model

The **f2clipboard** project turns Codex task pages and GitHub logs into clipboard-ready summaries.

## Current Snapshot (2025-09-29)

- **Operational context:** CLI and GitHub Action parse HTML/JSON, store cached data locally, and may
  contact Jira via optional plugins.
- **Key changes since 2025-09-24:** New modules (`secret.py`, plugin loaders) formalize token
  handling; prompt docs migrated to the Codex directory to guide automation.
- **Risks to monitor:** Local cache paths holding secrets, plugin authentication scopes, and GitHub
  Action runs operating with repository tokens.

## Threats

- **Credential leakage:** Cached transcripts or `.env` files could leak PATs.
- **HTML parsing attacks:** Malicious log payloads could trigger injection if sanitization fails.
- **Plugin overreach:** Third-party integrations (e.g., Jira) might request excessive permissions.

## Mitigations

- Encourage users to store credentials in OS keyrings or pass them via environment variables only at
  runtime.
- Continue expanding tests that cover log sanitization and plugin scope validation.
- Provide cleanup commands for local cache directories.
