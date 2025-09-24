# DSPACE Threat Model

DSPACE is an offline-first idle-sim that may integrate local automation tools.
This preliminary threat model documents basic assumptions.

## Current Snapshot (2025-09-24)

- **Gameplay loop:** Quest-based hobby tutorials delivered by NPC guides within a retro-futurist
  setting.
- **Offline emphasis:** Progress persists without connectivity, so local save handling deserves
  extra scrutiny.

## Security Assumptions

- Users run DSPACE on hardware they control.
- Quest data may be synced across devices by the user.

## Potential Risks

- Malicious quests or mods may escalate privileges.
- Save data could leak if stored in world-readable locations.
