# f2clipboard Threat Model

f2clipboard traverses directories and copies file paths to the clipboard.
This placeholder outlines potential security considerations.

## Current Snapshot (2025-09-24)

- **Workflow:** Parses Codex task descriptions and failure logs, then prepares a cleaned summary
  for quick sharing.
- **Primary risk:** Clipboard contents can expose sensitive CI logs or stack traces to other
  desktop apps—reinforcing the need for minimal retention.

## Security Assumptions

- Users run the tool locally with appropriate file permissions.
- Clipboard contents are ephemeral and may be intercepted by other apps.

## Potential Risks

- Processing untrusted directories could expose sensitive data.
- Copying huge file lists may freeze or crash the system.
