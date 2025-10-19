# gitshelves Threat Model

Gitshelves converts GitHub contribution data into printable shelf components using OpenSCAD.

## Current Snapshot (2025-10-18)

- **Operational context:** Python CLI fetches GitHub metadata, renders SCAD/STL assets, and packages
  docs explaining fabrication workflows.
- **Key changes since 2025-09-29:** PR #186 introduced Typer CLI commands, snapshot-tested SCAD
  outputs, and expanded docs, adding new dependency pathways.
- **Risks to monitor:** GitHub token permissions, SCAD rendering security (malicious geometry), and
  distribution of generated STLs without integrity checks.

## Threats

- **API abuse:** Stored tokens might leak or request more scopes than necessary.
- **Geometry injection:** User-supplied metadata could influence SCAD rendering if not sanitized.
- **Supply chain:** New CLI dependencies expand the attack surface.

## Mitigations

- Encourage personal access tokens with read-only scopes and document revocation steps.
- Sanitize contribution metadata before embedding it into SCAD templates.
- Keep dependencies pinned and run snapshot tests (`tests/test_scad.py`) to detect tampering.
