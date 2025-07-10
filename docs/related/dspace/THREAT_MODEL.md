# DSPACE Threat Model

DSPACE is an offline-first idle-sim that may integrate local automation tools.
This preliminary threat model documents basic assumptions.

## Security Assumptions

- Users run DSPACE on hardware they control.
- Quest data may be synced across devices by the user.

## Potential Risks

- Malicious quests or mods may escalate privileges.
- Save data could leak if stored in world-readable locations.
