# wove Threat Model

The **wove** project offers an open toolkit for learning textile crafts and evolving toward robotic
looms.

## Current Snapshot (2025-10-08)

- **Operational context:** Provides CAD/STL assets and a new crochet translation CLI for textile
  experimentation.
- **Key changes since 2025-09-29:** Translation CLI (PR #126) adds parsing of user-supplied patterns
  and new tests in CI.
- **Risks to monitor:** Parsing untrusted crochet patterns could cause denial-of-service or confusing
  instructions; ensure docs continue to emphasize mechanical safety when deploying outputs.

## Threats

- **Physical safety:** Misbuilt components could injure users.
- **Supply chain:** Third-party firmware or electronics could arrive compromised.
- **Documentation drift:** Stale docs may omit safety warnings or assembly checks.

## Mitigations

- Maintain docs that highlight PPE and tool requirements.
- Link to trusted firmware sources and note checksum verification steps.
- Add pre-flight checklists to CI to ensure safety docs stay bundled with CAD updates.
