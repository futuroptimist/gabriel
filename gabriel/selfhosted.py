"""Helpers for auditing self-hosted service configurations."""

from __future__ import annotations

import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Literal

Severity = Literal["low", "medium", "high"]


@dataclass(frozen=True, slots=True)
class CheckResult:
    """Represents a single configuration finding for a service."""

    slug: str
    message: str
    severity: Severity
    remediation: str


@dataclass(frozen=True, slots=True)
class VaultWardenConfig:
    """Configuration snapshot for a VaultWarden deployment."""

    https_enabled: bool
    certificate_trusted: bool
    encryption_key: str | None
    backup_enabled: bool
    backup_frequency_hours: int | None
    last_restore_verification_days: int | None
    admin_interface_enabled: bool = True
    admin_allowed_networks: Sequence[str] = ()


def audit_vaultwarden(config: VaultWardenConfig) -> list[CheckResult]:
    """Return security findings for a VaultWarden installation."""
    findings: list[CheckResult] = []

    if not config.https_enabled:
        findings.append(
            CheckResult(
                slug="vaultwarden-https",
                message="VaultWarden should be served over HTTPS with a trusted certificate.",
                severity="high",
                remediation=(
                    "Configure the reverse proxy or built-in TLS support to enforce HTTPS."
                ),
            )
        )
    elif not config.certificate_trusted:
        findings.append(
            CheckResult(
                slug="vaultwarden-https",
                message="HTTPS is enabled but the certificate is not trusted by clients.",
                severity="medium",
                remediation=(
                    "Install a certificate from a trusted CA or a well-known internal PKI."
                ),
            )
        )

    if not _is_strong_secret(config.encryption_key):
        findings.append(
            CheckResult(
                slug="vaultwarden-encryption-key",
                message=(
                    "Environment variable `VAULTWARDEN_ADMIN_TOKEN` or master key is weak or "
                    "unset."
                ),
                severity="high",
                remediation=(
                    "Provision a random token of at least 32 characters mixing cases, numbers, "
                    "and symbols."
                ),
            )
        )

    if not config.backup_enabled:
        findings.append(
            CheckResult(
                slug="vaultwarden-backups",
                message="Automatic backups are disabled.",
                severity="high",
                remediation="Enable recurring database backups and store them off-host.",
            )
        )
    else:
        if config.backup_frequency_hours is None or config.backup_frequency_hours > 24:
            findings.append(
                CheckResult(
                    slug="vaultwarden-backups",
                    message="Backups run infrequently. Aim for at least daily snapshots.",
                    severity="medium",
                    remediation="Schedule backups to run every 24 hours or more frequently.",
                )
            )
        if (
            config.last_restore_verification_days is None
            or config.last_restore_verification_days > 30
        ):
            findings.append(
                CheckResult(
                    slug="vaultwarden-restore-test",
                    message="Restore procedures have not been tested in the last 30 days.",
                    severity="medium",
                    remediation="Regularly test restoring from backups to verify integrity.",
                )
            )

    if config.admin_interface_enabled:
        if _is_network_list_open(config.admin_allowed_networks):
            findings.append(
                CheckResult(
                    slug="vaultwarden-admin-network",
                    message="Admin interface is reachable from untrusted networks.",
                    severity="high",
                    remediation="Restrict access to VPN ranges or internal subnets only.",
                )
            )
    return findings


@dataclass(frozen=True, slots=True)
class SyncthingConfig:
    """Configuration snapshot for a Syncthing deployment."""

    https_enabled: bool
    global_discovery_enabled: bool
    relays_enabled: bool
    connected_device_ids: Sequence[str]
    trusted_device_ids: Sequence[str]


def audit_syncthing(config: SyncthingConfig) -> list[CheckResult]:
    """Return security findings for a Syncthing installation."""
    findings: list[CheckResult] = []

    if not config.https_enabled:
        findings.append(
            CheckResult(
                slug="syncthing-https",
                message="Serve the Syncthing GUI over HTTPS behind a trusted reverse proxy.",
                severity="high",
                remediation="Terminate TLS before the GUI or enable Syncthing's built-in HTTPS.",
            )
        )

    if config.global_discovery_enabled:
        findings.append(
            CheckResult(
                slug="syncthing-global-discovery",
                message="Global discovery is enabled; disable it on trusted local networks.",
                severity="medium",
                remediation="Set global discovery to false so peers announce only locally.",
            )
        )

    if config.relays_enabled:
        findings.append(
            CheckResult(
                slug="syncthing-relays",
                message="Relay servers are enabled; disable relays when peers share trusted links.",
                severity="medium",
                remediation="Disable relays to avoid routing traffic through third parties.",
            )
        )

    normalized_connected = _normalize_device_ids(config.connected_device_ids)
    normalized_trusted = _normalize_device_ids(config.trusted_device_ids)

    if normalized_connected and not normalized_trusted:
        findings.append(
            CheckResult(
                slug="syncthing-trust-list",
                message="Connected devices exist but no trusted device allow-list is defined.",
                severity="medium",
                remediation="Keep an allow-list of expected device IDs and remove unknown peers.",
            )
        )
    else:
        unknown_devices = sorted(normalized_connected - normalized_trusted)
        if unknown_devices:
            device_list = ", ".join(unknown_devices)
            findings.append(
                CheckResult(
                    slug="syncthing-unknown-devices",
                    message=f"Syncthing is connected to unexpected device IDs: {device_list}.",
                    severity="high",
                    remediation="Remove unrecognized devices and rotate new IDs if necessary.",
                )
            )

    return findings


@dataclass(frozen=True, slots=True)
class NextcloudConfig:
    """Configuration snapshot for a self-hosted Nextcloud deployment."""

    https_enabled: bool
    certificate_trusted: bool
    mfa_enforced: bool
    updates_current: bool
    backups_enabled: bool
    last_backup_verification_days: int | None
    admin_allowed_networks: Sequence[str] = ()
    log_monitoring_enabled: bool = False


@dataclass(frozen=True, slots=True)
class PhotoPrismConfig:
    """Configuration snapshot for a PhotoPrism deployment."""

    https_enabled: bool
    certificate_trusted: bool
    admin_password: str | None
    library_outside_container: bool
    storage_permissions_hardened: bool
    backups_enabled: bool
    backup_frequency_days: int | None
    backups_offsite: bool
    third_party_plugins_enabled: bool
    plugins_reviewed: bool


def audit_nextcloud(config: NextcloudConfig) -> list[CheckResult]:
    """Return security findings for a Nextcloud installation."""
    findings: list[CheckResult] = []

    if not config.https_enabled:
        findings.append(
            CheckResult(
                slug="nextcloud-https",
                message="Nextcloud should be served over HTTPS with a trusted certificate.",
                severity="high",
                remediation="Configure HTTPS via a reverse proxy or the built-in TLS stack.",
            )
        )
    elif not config.certificate_trusted:
        findings.append(
            CheckResult(
                slug="nextcloud-https",
                message="HTTPS is enabled but the certificate is not trusted by clients.",
                severity="medium",
                remediation="Install a certificate from a trusted CA or internal PKI.",
            )
        )

    if not config.mfa_enforced:
        findings.append(
            CheckResult(
                slug="nextcloud-mfa",
                message="Require multi-factor authentication for all administrative users.",
                severity="high",
                remediation="Enable Nextcloud's MFA enforcement in the security settings.",
            )
        )

    if not config.updates_current:
        findings.append(
            CheckResult(
                slug="nextcloud-updates",
                message="Core or app updates are pending on the Nextcloud instance.",
                severity="medium",
                remediation=(
                    "Apply the latest Nextcloud and app updates before exposing the " "service."
                ),
            )
        )

    if not config.backups_enabled:
        findings.append(
            CheckResult(
                slug="nextcloud-backups",
                message="Automated backups are disabled for Nextcloud.",
                severity="high",
                remediation="Schedule recurring backups and store them on hardened storage.",
            )
        )
    else:
        restore_check_overdue = (
            config.last_backup_verification_days is None
            or config.last_backup_verification_days > 30
        )
        if restore_check_overdue:
            findings.append(
                CheckResult(
                    slug="nextcloud-restore-test",
                    message="Backup restore procedures have not been tested within 30 days.",
                    severity="medium",
                    remediation="Test restoring from backups monthly to verify integrity.",
                )
            )

    if _is_network_list_open(config.admin_allowed_networks):
        findings.append(
            CheckResult(
                slug="nextcloud-admin-network",
                message="Admin interface is reachable from untrusted networks.",
                severity="high",
                remediation="Restrict administrative access to VPN ranges or internal subnets.",
            )
        )

    if not config.log_monitoring_enabled:
        findings.append(
            CheckResult(
                slug="nextcloud-log-monitoring",
                message="Security log monitoring is disabled or not configured.",
                severity="medium",
                remediation="Enable log monitoring and alerting for suspicious Nextcloud activity.",
            )
        )

    return findings


def audit_photoprism(config: PhotoPrismConfig) -> list[CheckResult]:
    """Return security findings for a PhotoPrism installation."""
    findings: list[CheckResult] = []

    if not config.https_enabled:
        findings.append(
            CheckResult(
                slug="photoprism-https",
                message="PhotoPrism should be served over HTTPS with a trusted certificate.",
                severity="high",
                remediation="Terminate TLS before PhotoPrism or enable HTTPS in the container.",
            )
        )
    elif not config.certificate_trusted:
        findings.append(
            CheckResult(
                slug="photoprism-https",
                message="HTTPS is enabled but the certificate is not trusted by clients.",
                severity="medium",
                remediation="Install a certificate from a trusted CA or well-known internal PKI.",
            )
        )

    if not _is_strong_secret(config.admin_password):
        findings.append(
            CheckResult(
                slug="photoprism-admin-credentials",
                message="Admin credentials are weak or unset.",
                severity="high",
                remediation="Rotate the admin password to a random 32+ character secret.",
            )
        )

    if not config.library_outside_container:
        findings.append(
            CheckResult(
                slug="photoprism-library-storage",
                message="Originals library is stored inside the application container.",
                severity="medium",
                remediation=(
                    "Mount external storage for originals to preserve data during " "rebuilds."
                ),
            )
        )

    if not config.storage_permissions_hardened:
        findings.append(
            CheckResult(
                slug="photoprism-library-permissions",
                message="Library storage permissions are too permissive.",
                severity="medium",
                remediation=(
                    "Restrict filesystem permissions so only PhotoPrism can read " "originals."
                ),
            )
        )

    if not config.backups_enabled:
        findings.append(
            CheckResult(
                slug="photoprism-backups",
                message="Automated backups are disabled for PhotoPrism.",
                severity="high",
                remediation=(
                    "Schedule recurring database and originals backups to secure " "storage."
                ),
            )
        )
    else:
        if config.backup_frequency_days is None or config.backup_frequency_days > 1:
            findings.append(
                CheckResult(
                    slug="photoprism-backup-frequency",
                    message="Backups run infrequently. Aim for at least daily snapshots.",
                    severity="medium",
                    remediation=("Run PhotoPrism backups every 24 hours or more often."),
                )
            )
        if not config.backups_offsite:
            findings.append(
                CheckResult(
                    slug="photoprism-backup-location",
                    message="Backups are stored on the same host as PhotoPrism.",
                    severity="medium",
                    remediation=("Replicate backups to off-host or cloud storage with encryption."),
                )
            )

    if config.third_party_plugins_enabled and not config.plugins_reviewed:
        findings.append(
            CheckResult(
                slug="photoprism-plugins-review",
                message="Third-party plugins are enabled without security review.",
                severity="medium",
                remediation=(
                    "Audit each plugin for maintenance and security before enabling " "it."
                ),
            )
        )

    return findings


def _is_strong_secret(secret: str | None) -> bool:
    if not secret:
        return False
    if len(secret) < 32:
        return False
    classes = [
        re.search(r"[a-z]", secret),
        re.search(r"[A-Z]", secret),
        re.search(r"[0-9]", secret),
        re.search(r"[^A-Za-z0-9]", secret),
    ]
    return all(classes)


def _is_network_list_open(networks: Iterable[str]) -> bool:
    normalized = []
    for network in networks:
        candidate = network.strip()
        if not candidate:
            continue
        candidate_lower = candidate.lower()
        normalized.append(candidate_lower)
        if candidate_lower in {"*", "any", "0.0.0.0/0", "::/0"}:
            return True
    return not normalized


def _normalize_device_ids(device_ids: Sequence[str]) -> set[str]:
    normalized: set[str] = set()
    for device_id in device_ids:
        candidate = device_id.strip()
        if candidate:
            normalized.add(candidate.upper())
    return normalized


__all__ = [
    "CheckResult",
    "Severity",
    "VaultWardenConfig",
    "audit_vaultwarden",
    "SyncthingConfig",
    "audit_syncthing",
    "NextcloudConfig",
    "audit_nextcloud",
    "PhotoPrismConfig",
    "audit_photoprism",
]
