# danielsmith.io Threat Model

danielsmith.io is a Vite-powered Three.js scene deployed as a personal portfolio playground. This model captures
assumptions and security considerations for the project.

## Current Snapshot (2025-09-24)

- **Workflow:** Node-based toolchain (Vite, Vitest, ESLint) with CI enforcing linting, testing, docs, and smoke builds.
- **Touchpoints:** Serves a static site that may embed custom shaders, textures, and keyboard listeners.

## Security Assumptions

- GitHub Actions runs with least-privilege repository tokens and publishes only static assets.
- Third-party dependencies from npm remain within maintained version ranges and are audited before upgrades.
- The production hosting environment (e.g., Vercel, Netlify, or GitHub Pages) terminates TLS and enforces HTTPS redirects.

## Potential Risks

- Untrusted dependency updates (Three.js, Vite plugins) could introduce malicious scripts or supply-chain compromises.
- Keyboard controls without rate limiting or sanitization might allow unexpected key logging if reused in authenticated contexts.
- WebGL or shader features could expose excessive GPU usage or crash the browser on unsupported hardware.
- Absent content security policy headers leave the site more vulnerable to injected scripts during hosting misconfigurations.
