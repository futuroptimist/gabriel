# futuroptimist Threat Model

The `futuroptimist` repository orchestrates reproducible pipelines, datasets, and release assets
for the broader Futuroptimist ecosystem.

## Current Snapshot (2025-10-08)

- **Operational context:** Continues coordinating pipelines, roster checks, and outages while powering
  dependent repos.
- **Key changes since 2025-09-29:** New 01/02/03 CI workflows plus `update-repo-status.yml` automate
  lint/tests/docs and roster syncing (PR `docs: update repo statuses`).
- **Risks to monitor:** Additional workflows increase token usage—ensure PAT/OIDC secrets stay scoped
  and status polling handles API failures without leaking stack traces.

## Security Assumptions

- Pipelines run on managed infrastructure with restricted access to API keys and content assets.
- Contributors follow flywheel-style CI practices with mandatory linting and tests.

## Potential Risks

- Pipeline secrets (API keys, storage credentials) could leak through misconfigured CI or logs.
- Data artifacts might contain personally identifiable information from volunteers or collaborators.
- Cross-repo automation may trigger cascading failures if access tokens are over-permissioned.
