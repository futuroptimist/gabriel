# sugarkube Threat Model

The **sugarkube** project delivers an off-grid Raspberry Pi cluster platform with scripted
provisioning and rich documentation.

## Current Snapshot (2025-09-29)

- **Operational context:** Builds pi images, manages k3s clusters, and documents solar hardware.
- **Key changes since 2025-09-24:** Major documentation and script expansion introduced new CI
  workflows, QR code assets, and onboarding helpers.
- **Risks to monitor:** Credential handling in pi image builders, telemetry publishing scripts, and
  the growing number of workflow secrets.

## Threats

- **Secrets exposure:** Cloud-init files and scripts may embed API keys.
- **Supply chain:** Pi image dependencies and KiCad exports could be tampered with.
- **Operational drift:** Telemetry collectors or workflow bots might gain excessive privileges.

## Mitigations

- Keep `scripts/scan-secrets.py` and tests enforcing secret hygiene up to date.
- Document environment variables separately for local vs. CI image builds.
- Rotate tokens used by automation (Cloudflare, GitHub) and monitor audit logs for unusual access.
