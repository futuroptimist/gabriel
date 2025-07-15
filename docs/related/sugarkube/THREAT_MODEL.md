# sugarkube Threat Model

sugarkube automates infrastructure deployments. This outline describes assumed risks and mitigations when using the tool.

## Security Assumptions

- Users run sugarkube on hardware they control.
- Deployments may target cloud environments with sensitive credentials.

## Potential Risks

- Leaked secrets in deployment configuration files.
- Misconfigured access controls in generated infrastructure.

## Mitigations

- Keep sensitive values in environment variables or secret stores.
- Review generated resources for least-privilege permissions.
