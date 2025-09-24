# sugarkube Threat Model

sugarkube automates infrastructure deployments. This outline describes assumed risks and mitigations when using the tool.

## Current Snapshot (2025-09-24)

- **Deployment target:** Solar-assisted Raspberry Pi clusters orchestrated with k3s for
  off-grid experimentation.
- **Operational concerns:** Edge environments may lack physical security and reliable power,
  increasing the need for tamper-resistant configs.

## Security Assumptions

- Users run sugarkube on hardware they control.
- Deployments may target cloud environments with sensitive credentials.

## Potential Risks

- Leaked secrets in deployment configuration files.
- Misconfigured access controls in generated infrastructure.

## Mitigations

- Keep sensitive values in environment variables or secret stores.
- Review generated resources for least-privilege permissions.
