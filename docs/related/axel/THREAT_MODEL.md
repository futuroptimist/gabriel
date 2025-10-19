# Axel Threat Model

Axel analyzes repositories, coordinates automation quests, and bridges multiple Futuroptimist
projects.

## Current Snapshot (2025-10-18)

- **Operational context:** CLI and Discord bot orchestrate repo scans, merge policies, and hillclimb
  automations driven by `.axel/` scripts.
- **Key changes since 2025-09-29:** PR #210 added JSON exports, a full Discord bot implementation, and
  token.place integrations, greatly expanding automation breadth and secret usage.
- **Risks to monitor:** Discord bot tokens, local `local/` artifacts, and cross-repo operations that
  might leak privileged data.

## Threats

- **Token exposure:** Discord bot credentials could leak via logs or incorrectly scoped permissions.
- **Cross-repo mutations:** Automation that writes to other repos risks propagating secrets or
  misconfigurations.
- **Local artifact leakage:** Hillclimb scripts store repo metadata in `local/`, which may include
  cached prompts or tokens.

## Mitigations

- Enforce `.gitignore` coverage for `local/` paths and document secure storage expectations.
- Rotate Discord bot tokens regularly and apply least-privilege scopes.
- Gate cross-repo operations behind dry runs and policy checks to prevent accidental pushes.
