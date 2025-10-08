# danielsmith.io Threat Model

The **danielsmith.io** project serves a Three.js-powered interactive portfolio site.

## Current Snapshot (2025-10-08)

- **Operational context:** Static Vite/Three.js build with accessibility-focused HUD cues and
  screenshot automation.
- **Key changes since 2025-09-29:** Live-region focus announcements (PR #111) augment DOM updates and
  require careful sanitization.
- **Risks to monitor:** Ensure aria-live regions do not expose debug strings and continue auditing
  screenshot artifacts for sensitive content.

## Threats

- **Asset leakage:** Resume PDFs or textures may contain sensitive personal information.
- **Automation misuse:** Playwright workflows could leak GitHub tokens if misconfigured.
- **Dependency drift:** Vite/Three.js dependencies might introduce vulnerabilities.

## Mitigations

- Keep resume assets reviewed for PII before committing.
- Store workflow artifacts in private buckets and limit retention time.
- Use Dependabot and security audits to keep npm dependencies patched.
