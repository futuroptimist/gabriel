# wove Threat Model

The **wove** project offers an open toolkit for learning textile crafts and evolving toward robotic
looms.

## Current Snapshot (2025-09-29)

- **Operational context:** Hosts CAD files, STL exports, and documentation describing the knitting
  machine builds.
- **Key changes since 2025-09-24:** Large documentation and STL drop fleshed out assembly steps;
  automation now includes lint/tests/docs pipelines.
- **Risks to monitor:** Safety guidance for mechanical builds and the potential inclusion of unsafe
  wiring instructions.

## Threats

- **Physical safety:** Misbuilt components could injure users.
- **Supply chain:** Third-party firmware or electronics could arrive compromised.
- **Documentation drift:** Stale docs may omit safety warnings or assembly checks.

## Mitigations

- Maintain docs that highlight PPE and tool requirements.
- Link to trusted firmware sources and note checksum verification steps.
- Add pre-flight checklists to CI to ensure safety docs stay bundled with CAD updates.
