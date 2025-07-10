# f2clipboard Threat Model

f2clipboard traverses directories and copies file paths to the clipboard.
This placeholder outlines potential security considerations.

## Security Assumptions

- Users run the tool locally with appropriate file permissions.
- Clipboard contents are ephemeral and may be intercepted by other apps.

## Potential Risks

- Processing untrusted directories could expose sensitive data.
- Copying huge file lists may freeze or crash the system.
