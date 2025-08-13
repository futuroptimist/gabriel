---
title: Update Flywheel Risk Model
slug: update-risk-model
evergreen: true
one_click: false
---

# Update Flywheel Risk Model
Type: evergreen

Assess how a proposed change affects the risk landscape described in
`docs/gabriel/FLYWHEEL_RISK_MODEL.md`.

```
SYSTEM: You are a security reviewer for the futuroptimist/gabriel repository.

USER:
Purpose:
- Examine the change description or diff and update the risk model.

CONTEXT:
<insert description of the change or diff>

TASKS:
1. Determine which sections of the risk model need updates.
2. Propose wording for new risks or mitigations.
3. Flag any areas requiring human review.

OUTPUT:
Provide updated passages ready to merge into
`docs/gabriel/FLYWHEEL_RISK_MODEL.md`.
```
