# sigma Threat Model

The **sigma** project builds a local-first ESP32 AI pin with voice interaction.

## Current Snapshot (2025-10-08)

- **Operational context:** Sigma continues to ship CAD models, Python firmware utilities, and prompt
  guides for the ESP32 wearable.
- **Key changes since 2025-09-29:** Nested LLM segment parsing landed (PR #131) and GitHub workflows
  were split for lint/tests, touching CI permissions.
- **Risks to monitor:** Parsing changes ingest more user content—validate escaping for spoken prompts
  and confirm workflow secrets stay scoped as pipelines multiply.

## Threats

- **Hardware tampering:** STL files or SCAD macros could be modified maliciously.
- **Firmware compromise:** Scripts interacting with the ESP32 may flash untrusted binaries.
- **Privacy leakage:** Voice logs or telemetry could leak if future integrations add cloud sync.

## Mitigations

- Provide checksums or signed releases for STL files.
- Recommend flashing firmware from trusted, versioned sources.
- Encourage builders to keep inference local and explicitly opt into any telemetry collection.
