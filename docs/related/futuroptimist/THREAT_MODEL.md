# futuroptimist Threat Model

The `futuroptimist` repository orchestrates reproducible pipelines, datasets, and release assets
for the broader Futuroptimist ecosystem.

## Current Snapshot (2025-09-29)

- **Operational context:** Coordinates scripts, runbooks, and outage reports that keep the YouTube
  production pipeline healthy while feeding dependent projects such as `flywheel`, `token.place`,
  and `gabriel`.
- **Key changes since 2025-09-24:** README gains an hourly roster refresh workflow to highlight
  stale dependencies; no privileged services were added.
- **Risks to monitor:** Workflow secrets used by publishing scripts, storage of media artifacts,
  and access tokens shared with downstream automation.

## Security Assumptions

- Pipelines run on managed infrastructure with restricted access to API keys and content assets.
- Contributors follow flywheel-style CI practices with mandatory linting and tests.

## Potential Risks

- Pipeline secrets (API keys, storage credentials) could leak through misconfigured CI or logs.
- Data artifacts might contain personally identifiable information from volunteers or collaborators.
- Cross-repo automation may trigger cascading failures if access tokens are over-permissioned.
