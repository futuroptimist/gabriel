# Improvement Checklists

This page consolidates security and feature enhancements suggested for repositories related to Gabriel. Each item is written as a task that could be implemented by contributors.

## token.place

- [ ] Enforce per-client rate limiting to mitigate DoS and Sybil attacks.
- [ ] Require relay and server node authentication before joining the network.
- [ ] Rotate relay and server certificates on a regular schedule.
- [ ] Sign relay binaries so clients can verify integrity.
- [ ] Provide optional server-side hooks for content moderation after decryption.
- [ ] Document how to keep moderation logic separate from relay code.
- [ ] Disable verbose logs in production and strip connection metadata.
- [ ] Offer an audit mode for temporary debugging.
- [ ] Engage third-party security auditors to review the protocol and codebase.
- [ ] Publish audit findings and follow up with patches as needed.

## PhotoPrism

- [ ] Enable HTTPS by default and use strong admin credentials.
- [ ] Store images outside of the application container with strict permissions.
- [ ] Set up scheduled backups to a secure location.
- [ ] Review third-party plugins for security issues before enabling them.

## VaultWarden

- [ ] Serve the interface over HTTPS with a trusted certificate.
- [ ] Configure environment variables for strong encryption keys.
- [ ] Enable automatic database backups and verify restore procedures.
- [ ] Restrict admin interface access to trusted networks or VPN.

## sigma

- [ ] Prototype a push-to-talk interface for local LLM interaction.
- [ ] Keep all audio processing local to preserve privacy.
- [ ] Document simple installation steps so Gabriel users can try sigma.

## axel

- [ ] Document `.gitignore` verification for `local/` directories
- [ ] Provide token rotation guidance in docs
- [ ] Add THREAT_MODEL.md with cross-repo considerations
- [ ] Explore encrypting `local/discord/` notes
- [ ] Review permissions for integrated tools (token.place, gabriel)

