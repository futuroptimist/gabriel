# wove Threat Model

Wove provides tooling for learning textiles while moving toward robotic looms.

## Current Snapshot (2025-10-18)

- **Operational context:** Python CLI renders patterns, OpenSCAD models deliver hardware fixtures, and
  docs guide users through manual-to-robotic workflows.
- **Key changes since 2025-09-29:** Pattern visualization harness (PR #158) introduced new scripts,
  schemas, and STL assets, increasing inputs accepted from users.
- **Risks to monitor:** Pattern JSON ingestion, local file rendering, and distribution of STL assets
  without integrity metadata.

## Threats

- **Malicious patterns:** Crafted pattern files could exploit visualization scripts if parsing is lax.
- **Hardware tampering:** Unverified STL downloads may be swapped with unsafe designs.
- **Doc drift:** Incorrect setup docs might leave machines running without mandated safety checks.

## Mitigations

- Validate pattern schemas strictly and document safe directories for CLI imports.
- Publish SHA256 checksums for STL bundles and encourage verification prior to printing.
- Keep safety and gauge documentation versioned to discourage unsafe overrides.
