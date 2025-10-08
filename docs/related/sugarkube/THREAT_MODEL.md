# sugarkube Threat Model

The **sugarkube** project delivers an off-grid Raspberry Pi cluster platform with scripted
provisioning and rich documentation.

## Current Snapshot (2025-10-08)

- **Operational context:** Continues to orchestrate Raspberry Pi k3s clusters with Python automation
  and extensive documentation.
- **Key changes since 2025-09-29:** README and doc-test refresh (PR #1192) tied doc guidance to
  executable tests and reworked coverage thresholds.
- **Risks to monitor:** Doc tests rely on local commands—ensure they avoid leaking environment
  variables or credentials during CI runs.

## Threats

- **Secrets exposure:** Cloud-init files and scripts may embed API keys.
- **Supply chain:** Pi image dependencies and KiCad exports could be tampered with.
- **Operational drift:** Telemetry collectors or workflow bots might gain excessive privileges.

## Mitigations

- Keep `scripts/scan-secrets.py` and tests enforcing secret hygiene up to date.
- Document environment variables separately for local vs. CI image builds.
- Rotate tokens used by automation (Cloudflare, GitHub) and monitor audit logs for unusual access.
