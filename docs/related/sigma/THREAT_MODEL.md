# sigma Threat Model

The **sigma** project builds a local-first ESP32 AI pin with voice interaction.

## Current Snapshot (2025-09-29)

- **Operational context:** CAD designs and Python control scripts guide the open hardware build.
- **Key changes since 2025-09-24:** Prompt docs relocated and hardware documentation expanded; core
  firmware paths remain offline.
- **Risks to monitor:** Hardware supply chain (printed parts vs. purchased electronics) and
  documentation that might encourage unsafe power configurations.

## Threats

- **Hardware tampering:** STL files or SCAD macros could be modified maliciously.
- **Firmware compromise:** Scripts interacting with the ESP32 may flash untrusted binaries.
- **Privacy leakage:** Voice logs or telemetry could leak if future integrations add cloud sync.

## Mitigations

- Provide checksums or signed releases for STL files.
- Recommend flashing firmware from trusted, versioned sources.
- Encourage builders to keep inference local and explicitly opt into any telemetry collection.
