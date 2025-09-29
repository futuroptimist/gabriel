# danielsmith.io Threat Model

The **danielsmith.io** project serves a Three.js-powered interactive portfolio site.

## Current Snapshot (2025-09-29)

- **Operational context:** Static Vite build with Playwright-driven screenshot automation and
  TypeScript source.
- **Key changes since 2025-09-24:** Screenshot workflow refreshed launch imagery; no new APIs or
  services were integrated.
- **Risks to monitor:** Handling of resume data, screenshot storage, and any analytics integrations.

## Threats

- **Asset leakage:** Resume PDFs or textures may contain sensitive personal information.
- **Automation misuse:** Playwright workflows could leak GitHub tokens if misconfigured.
- **Dependency drift:** Vite/Three.js dependencies might introduce vulnerabilities.

## Mitigations

- Keep resume assets reviewed for PII before committing.
- Store workflow artifacts in private buckets and limit retention time.
- Use Dependabot and security audits to keep npm dependencies patched.
