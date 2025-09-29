# flywheel Threat Model

The **flywheel** template helps repos bootstrap linting, testing, docs, and CAD workflows.

## Current Snapshot (2025-09-29)

- **Operational context:** Provides a baseline CI/CD stack (lint, tests, docs, security scan) and
  status reporting for downstream projects.
- **Key changes since 2025-09-24:** Repository roster docs were refreshed; automation, templates,
  and CAD assets remain the same.
- **Risks to monitor:** Secrets in GitHub Actions, large binary artifacts in STL exports, and the
  nightly scanning scripts that enumerate dependent repos.

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
