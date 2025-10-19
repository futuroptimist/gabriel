# DSPACE Threat Model

The **DSPACE** repository powers the democratized.space quest platform, combining offline-first
content with rich quest data.

## Current Snapshot (2025-10-18)

- **Operational context:** Frontend and backend bundles ship through pnpm with automated quest
  validation, outage tracking, and monitoring hooks.
- **Key changes since 2025-09-29:** The `v3` branch landed a stream of quest-ingestion fixes,
  offline cache hardening, and CLI clean-up merges that still await a stable tag, increasing review
  load while the team keeps the pipelines healthy and documentation accurate.
- **Risks to monitor:** Asset provenance, secrets embedded in quest metadata, and telemetry scripts
  that might expand analytics scope.

## Threats

- **Supply chain:** Compromised pnpm packages or quest bundles could distribute malicious assets.
- **Data leakage:** Quest submissions or telemetry could capture personal data if schemas drift.
- **CI exfiltration:** GitHub Actions workflows run quest validators and could expose tokens if
  logs are verbose.

## Mitigations

- Pin dependencies in `pnpm-lock.yaml` and review diff noise before upgrades.
- Keep quest validation and `scripts/checkPatchCoverage.cjs` up to date to reject malformed content.
- Limit secrets in CI to least privilege and redact quest telemetry in logs.
