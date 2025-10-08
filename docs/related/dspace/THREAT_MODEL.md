# DSPACE Threat Model

The **DSPACE** repository powers the democratized.space quest platform, combining offline-first
content with rich quest data.

## Current Snapshot (2025-10-08)

- **Operational context:** v3 continues to ship pnpm-built Astro/Svelte bundles with achievements
  tracking and offline-first quest data backed by automated validators.
- **Key changes since 2025-09-29:** Achievements rollout (PR #1937) layered new quest metadata,
  Docker packaging, and CI workflows that touch deployment credentials.
- **Risks to monitor:** Larger asset inventories widen supply-chain risk, and new achievements data
  paths could leak personal progress if analytics scripts expand unchecked.

## Threats

- **Supply chain:** Compromised pnpm packages or quest bundles could distribute malicious assets.
- **Data leakage:** Quest submissions or telemetry could capture personal data if schemas drift.
- **CI exfiltration:** GitHub Actions workflows run quest validators and could expose tokens if
  logs are verbose.

## Mitigations

- Pin dependencies in `pnpm-lock.yaml` and review diff noise before upgrades.
- Keep quest validation and `scripts/checkPatchCoverage.cjs` up to date to reject malformed content.
- Limit secrets in CI to least privilege and redact quest telemetry in logs.
