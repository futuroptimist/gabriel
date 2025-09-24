# sigma Threat Model

sigma is an open-source AI pin device for local voice interactions.
This tentative threat model outlines security considerations.

## Current Snapshot (2025-09-24)

- **Form factor:** ESP32-based wearable with push-to-talk activation and on-device inference.
- **Privacy promise:** Speech-to-text, LLM, and TTS all execute locally to keep voice commands
  offline unless explicitly synced.

## Security Assumptions

- The device processes audio locally and stores data on-device.
- Network connectivity is optional and user-controlled.

## Potential Risks

- Stolen devices could expose recorded audio if not encrypted.
- Firmware updates may be a vector for supply chain attacks.
