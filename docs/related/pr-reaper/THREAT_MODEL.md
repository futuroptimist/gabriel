# pr-reaper Threat Model

The **pr-reaper** tool automates closing stale pull requests in bulk.

## Current Snapshot (2025-10-08)

- **Operational context:** CLI/GitHub Action sweeps stale PRs using PATs with repo scopes.
- **Key changes since 2025-09-29:** Workflow overhaul (PR #34) introduced dedicated close-my-open-prs
  automation and CI hygiene files.
- **Risks to monitor:** New workflow adds concurrency—confirm dry-run toggles and branch filters stay
  conservative to prevent accidental closures.

## Threats

- **Token misuse:** Leaked PATs could let attackers close or modify PRs.
- **Mass closure accidents:** Misconfigured filters may close active PRs.
- **Workflow escalation:** GitHub Actions might gain write access beyond intention.

## Mitigations

- Encourage fine-grained PATs or GitHub Apps with repository-specific scopes.
- Keep dry-run mode on by default and require explicit confirmation for destructive runs.
- Log actions to provide audit trails when sweeping PRs.
