# flywheel Threat Model

flywheel offers a standardized setup for reproducible releases.
This placeholder covers initial considerations.

## Security Assumptions

- Maintainers run CI on trusted GitHub infrastructure.
- Secrets for releases are stored as encrypted repository secrets.

## Potential Risks

- Misconfigured CI could leak tokens via logs.
- Build artifacts might include sensitive files if not filtered.
