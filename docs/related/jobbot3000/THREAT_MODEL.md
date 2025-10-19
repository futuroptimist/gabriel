# jobbot3000 Threat Model

Jobbot3000 is a self-hosted job search copilot with CLI, web UI, and automation scripts.

## Current Snapshot (2025-10-18)

- **Operational context:** Node services ingest listings, enrich resumes, and expose dashboards and CLI
  entry points.
- **Key changes since 2025-09-29:** PR #835 enabled the native CLI inside docker-compose stacks and
  landed significant docs/tests, broadening deployment options and surface area.
- **Risks to monitor:** Provider API tokens, analytics data stored on disk, and new web endpoints served
  from docker-compose bundles.

## Threats

- **Credential sprawl:** `.env.example` hints at many provider tokens that must remain scoped.
- **Data leakage:** Analytics exports and resume processing may store sensitive user data.
- **Service exposure:** The web server now ships in docker-compose, increasing attack surface.

## Mitigations

- Document least-privilege API scopes and rotation schedules for provider integrations.
- Provide cleanup scripts for analytics artifacts and redact PII before export.
- Require TLS proxies and authentication in front of the docker-compose web service by default.
