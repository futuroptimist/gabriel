# sigma Threat Model

Sigma is an ESP32-powered AI pin with voice input, LLM calls, and local TTS playback.

## Current Snapshot (2025-10-18)

- **Operational context:** Firmware, Python orchestration, and web viewers coordinate on-device
  inference, audio capture, and 3D visualization.
- **Key changes since 2025-09-29:** PR #173 added Whisper endpoint overrides and bundled new Three.js
  assets, increasing dependency footprints but improving configurability.
- **Risks to monitor:** Network access to alternate Whisper servers, embedded credentials in firmware,
  and supply-chain integrity for large JS bundles.

## Threats

- **Firmware compromise:** Unsigned binaries could allow malicious payloads on the ESP32.
- **Network eavesdropping:** Whisper traffic routed to remote servers may expose sensitive voice data.
- **Web viewer exploits:** Bundled Three.js assets could harbor vulnerabilities if not kept current.

## Mitigations

- Sign firmware builds and publish checksum manifests for users to verify downloads.
- Encourage local Whisper deployments or TLS-enforced endpoints when overrides are enabled.
- Track upstream Three.js advisories and refresh vendor bundles promptly.
