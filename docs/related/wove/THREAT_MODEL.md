# wove Threat Model

wove drives robotic looms to knit custom patterns. This placeholder outlines basic assumptions.

## Current Snapshot (2025-09-24)

- **Roadmap:** Teaching manual knitting/crochet today while iterating toward semi-automated or
  robotic looms in the future.
- **Digital pipeline:** Bridges CAD-derived stitch patterns with textile hardware, implying a mix
  of software and electromechanical risk.

## Security Assumptions

- Users connect wove to hardware they control.
- Pattern files may be shared publicly or kept private.

## Potential Risks

- Remote control features could damage hardware if misused.
- Malformed pattern files might cause jams or wasted materials.
