# sigma Threat Model

sigma is an open-source AI pin device for local voice interactions.
This tentative threat model outlines security considerations.

## Security Assumptions

- The device processes audio locally and stores data on-device.
- Network connectivity is optional and user-controlled.

## Potential Risks

- Stolen devices could expose recorded audio if not encrypted.
- Firmware updates may be a vector for supply chain attacks.
