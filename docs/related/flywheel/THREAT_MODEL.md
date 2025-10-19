# flywheel Threat Model

The `flywheel` template helps small teams ship production-grade automation with linting, testing,
and release pipelines baked in.

## Current Snapshot (2025-10-18)

- **Operational context:** Provides reusable CI/CD scaffolding, docs, and CAD assets for companion
  projects such as `gabriel`, `token.place`, and `axel`.
- **Key changes since 2025-09-29:** Docs refresh (86f4f03) updated the feature summary; runtime code
  and workflows remain unchanged.
- **Risks to monitor:** Reusable GitHub Actions secrets, templated infra scripts, and CAD assets that
  downstream repos compile automatically.

## Threats

- **Supply chain:** Consumers inherit dependencies defined in `pyproject.toml`, `package.json`, and
  CI templates. A compromise could ripple through downstream repos.
- **Documentation drift:** Outdated docs may cause misconfigured deployments that weaken security.
- **Credential leakage:** Shared onboarding scripts might encourage insecure storage of API keys.

## Mitigations

- Keep dependency pins current and scan with `pip-audit`/`npm audit` before publishing template
  updates.
- Document secret management best practices explicitly in onboarding checklists.
- Continue running CodeQL and other CI checks to catch regressions early.
