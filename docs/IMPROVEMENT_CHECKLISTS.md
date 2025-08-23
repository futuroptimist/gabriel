# Improvement Checklists

This page consolidates security and feature enhancements suggested for repositories related to Gabriel.
Where a dedicated document exists, follow the link below. Otherwise tasks are listed inline.

## Gabriel (self)
See [gabriel/IMPROVEMENTS.md](gabriel/IMPROVEMENTS.md).

## token.place
See [related/token_place/IMPROVEMENTS.md](related/token_place/IMPROVEMENTS.md).

## DSPACE
See [related/dspace/IMPROVEMENTS.md](related/dspace/IMPROVEMENTS.md).

## flywheel
See [related/flywheel/IMPROVEMENTS.md](related/flywheel/IMPROVEMENTS.md).

## f2clipboard
See [related/f2clipboard/IMPROVEMENTS.md](related/f2clipboard/IMPROVEMENTS.md).

## axel
See [related/axel/IMPROVEMENTS.md](related/axel/IMPROVEMENTS.md).

## sigma
See [related/sigma/IMPROVEMENTS.md](related/sigma/IMPROVEMENTS.md).

## gitshelves
See [related/gitshelves/IMPROVEMENTS.md](related/gitshelves/IMPROVEMENTS.md).

## wove
See [related/wove/IMPROVEMENTS.md](related/wove/IMPROVEMENTS.md).

## sugarkube
See [related/sugarkube/IMPROVEMENTS.md](related/sugarkube/IMPROVEMENTS.md).

## Nextcloud
See [related/nextcloud/IMPROVEMENTS.md](related/nextcloud/IMPROVEMENTS.md).

## PhotoPrism
- [ ] Enable HTTPS by default and use strong admin credentials.
- [ ] Store images outside of the application container with strict permissions.
- [ ] Set up scheduled backups to a secure location.
- [ ] Review third-party plugins for security issues before enabling them.

## Syncthing
- [ ] Serve GUI over HTTPS via reverse proxy ([docs](https://docs.syncthing.net/users/https.html)).
- [ ] Disable global discovery and relays on trusted networks
  ([docs](https://docs.syncthing.net/users/discovery.html)).
- [ ] Audit IDs and remove unknown connections ([repo](https://github.com/syncthing/syncthing)).

## VaultWarden
- [ ] Serve the interface over HTTPS with a trusted certificate.
- [ ] Configure environment variables for strong encryption keys.
- [ ] Enable automatic database backups and verify restore procedures.
- [ ] Restrict admin interface access to trusted networks or VPN.
