# f2clipboard Threat Model

The **f2clipboard** project turns Codex task pages and GitHub logs into clipboard-ready summaries.

## Current Snapshot (2025-10-08)

- **Operational context:** Python CLI/GitHub Action continues to parse Codex pages and logs while
  caching results locally and syncing optional Slack/Jira integrations.
- **Key changes since 2025-09-29:** Automation for applying LLM-generated merge patches (PR #158)
  now interacts with Git data and GitHub tokens.
- **Risks to monitor:** Merge patch automation broadens the risk of executing untrusted diffs, and
  caches still need periodic scrubbing to avoid credential persistence.

## Threats

- **Credential leakage:** Cached transcripts or `.env` files could leak PATs.
- **HTML parsing attacks:** Malicious log payloads could trigger injection if sanitization fails.
- **Plugin overreach:** Third-party integrations (e.g., Jira) might request excessive permissions.

## Mitigations

- Encourage users to store credentials in OS keyrings or pass them via environment variables only at
  runtime.
- Continue expanding tests that cover log sanitization and plugin scope validation.
- Provide cleanup commands for local cache directories.
