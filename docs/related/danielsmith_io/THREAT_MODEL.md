# danielsmith.io Threat Model

The `danielsmith.io` repository hosts a personal portfolio built with Vite and Three.js.

## Current Snapshot (2025-10-18)

- **Operational context:** Static site served from a Vite build, showcasing 3D scenes and media assets.
- **Key changes since 2025-09-29:** Commit 2f1e29e refreshed a launch screenshot; no runtime code was
  modified.
- **Risks to monitor:** Third-party model imports, asset licensing, and browser security headers.

## Threats

- **Asset poisoning:** Replacing hosted textures or models could compromise the scene.
- **Script vulnerabilities:** Outdated Three.js releases may contain XSS or sandbox escapes.
- **Privacy concerns:** Embedded analytics or media might leak personal data if misconfigured.

## Mitigations

- Pin Three.js versions and audit dependencies before deployment.
- Serve via TLS with strict CSP and disable inline scripts where possible.
- Review assets for licensing and privacy implications before publishing updates.
