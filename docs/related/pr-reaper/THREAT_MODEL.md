# pr-reaper Threat Model

pr-reaper closes stale pull requests owned by the repository maintainer.

## Current Snapshot (2025-10-18)

- **Operational context:** GitHub Action written in TypeScript compiles to `dist/` JavaScript and runs
  in GitHub-hosted or self-hosted runners.
- **Key changes since 2025-09-29:** PR #51 ensures composite inputs flow to the runtime environment,
  clarifying configuration and reducing accidental no-ops.
- **Risks to monitor:** Repository or workflow secrets forwarded to the action, GitHub API rate limits,
  and potential misuse on repositories without proper filtering.

## Threats

- **Overbroad deletion:** Misconfigured filters could close active PRs.
- **Secret leakage:** Inputs passed to the runtime may include secrets if consumers misconfigure their
  workflows.
- **Supply chain:** Dependencies for building `dist/` might introduce vulnerabilities.

## Mitigations

- Document conservative defaults and encourage dry runs before closing PRs.
- Mask sensitive inputs and avoid logging token values.
- Keep dependencies pinned and run `npm audit` before releasing new action bundles.
