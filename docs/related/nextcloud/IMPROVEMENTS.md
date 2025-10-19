# Nextcloud Hardening Checklist

This document outlines basic security steps for self-hosted Nextcloud. The project is no longer on the
Futuroptimist related-project roster as of the 2025-10-18 sync, but Gabriel keeps this checklist for
self-hosting references.

## Current Snapshot (2025-10-18)

- **Status:** Not tracked on the Futuroptimist roster; checklist retained for self-hosted guidance.
- **Watchlist:** TLS configuration, MFA coverage, update cadence, and admin interface exposure remain
  the top risks when deploying community-run Nextcloud instances.

## Checklist

- [ ] Serve Nextcloud over HTTPS with a trusted certificate.
- [ ] Enable multi-factor authentication for all users.
- [ ] Schedule regular backups and test restore procedures.
- [ ] Keep Nextcloud and its apps updated promptly.
- [ ] Restrict admin interface access to trusted networks.
- [ ] Monitor logs for suspicious activity.

Gabriel now offers `gabriel.selfhosted.audit_nextcloud` to check these controls and provide
remediation guidance for common hardening gaps.
