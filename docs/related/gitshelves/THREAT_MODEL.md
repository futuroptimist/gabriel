# gitshelves Threat Model

gitshelves turns GitHub contribution data into 3D-printable blocks.
This short threat model notes a few considerations.

## Current Snapshot (2025-09-24)

- **Workflow:** Converts contribution graphs into STL files sized for 42 mm Gridfinity baseplates.
- **Data sensitivity:** Even "public" contribution heatmaps may expose working hours or private
  repository cadence when aggregated.

## Security Assumptions

- Users authenticate via GitHub APIs to fetch public data.
- Generated models are shared at the user's discretion.

## Potential Risks

- Authentication tokens may leak if stored insecurely.
- Downloaded contribution data could reveal activity patterns.
