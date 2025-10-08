# flywheel Threat Model

The **flywheel** template helps repos bootstrap linting, testing, docs, and CAD workflows.

## Current Snapshot (2025-10-08)

- **Operational context:** Continues to serve as the bootstrap template for lint/test/docs pipelines
  and RepoCrawler-driven portfolio reports.
- **Key changes since 2025-09-29:** PR #626 now flags RepoCrawler API errors as failures, raising
  visibility into stalled CI on downstream repositories.
- **Risks to monitor:** Increased error sensitivity could throttle the status dashboard if GitHub
  outages persist, and RepoCrawler still relies on PAT scopes that need regular review.

## Threats

- **Supply chain:** npm and Python dependencies may be hijacked.
- **Credential leakage:** Docs and scripts show how to integrate PATs; misconfiguration can leak
  tokens.
- **Artifact tampering:** Generated STL/GLB files could contain malicious payloads if the build
  pipeline is compromised.

## Mitigations

- Keep `dependabot` and lockfiles current.
- Use GitHub environments or OpenID Connect for workflows that need secrets.
- Require reviews on prompt-doc updates and STL changes to detect suspicious diffs.
