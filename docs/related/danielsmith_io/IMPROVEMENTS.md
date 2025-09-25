# Suggested Improvements for danielsmith.io

This document tracks enhancement ideas for the [danielsmith.io](https://github.com/futuroptimist/danielsmith.io) repository.

## Current Snapshot (2025-09-24)

- **Status:** Newly added to the Futuroptimist related projects list.
- **Focus:** Vite + Three.js playground for an isometric personal site experience with keyboard controls.
- **Primary integration:** Shares Flywheel-style automation (lint, tests, docs) while experimenting with spatial UX.

## Checklist

- [ ] Add accessibility affordances such as focus outlines, reduced-motion toggles, and screen reader copy for the 3D scene.
- [ ] Expand input handling beyond keyboard to cover touch/gamepad per the backlog roadmap, guarding against duplicate event firing.
- [ ] Document and automate WebGL capability fallbacks (e.g., static render, explanatory copy) inside the smoke test workflow.
- [ ] Capture lightweight visual regression snapshots during `npm run smoke` to detect unintended material/light changes.
