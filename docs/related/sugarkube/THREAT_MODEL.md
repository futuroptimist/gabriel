# sugarkube Threat Model

Sugarkube packages solar-powered Raspberry Pi clusters with Kubernetes, imaging scripts, and
hardware plans.

## Current Snapshot (2025-10-18)

- **Operational context:** GitHub Actions build Pi images, render CAD, and publish docs; scripts manage
  telemetry, token.place samples, and hardware provisioning.
- **Key changes since 2025-09-29:** Vision doc refresh (PR #1348) added telemetry helpers, QR assets,
  and additional workflows, expanding automation complexity while CI currently reports red.
- **Risks to monitor:** Sensitive telemetry data in artifacts, Pi image credentials, and long-lived
  GitHub tokens driving imaging pipelines.

## Threats

- **Artifact leakage:** Pi images may embed credentials if build scripts collect secrets from the
  environment.
- **Telemetry exposure:** Workflow notifiers could post sensitive logs externally if misconfigured.
- **Build system compromise:** Extensive GitHub Actions surface increases attack opportunities.

## Mitigations

- Enforce secret scanning and artifact scrubbing in imaging workflows.
- Limit telemetry destinations to trusted endpoints and document anonymization steps.
- Stabilize CI pipelines and apply least-privilege policies to GitHub tokens used during builds.
