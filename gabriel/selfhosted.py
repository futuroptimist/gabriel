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
class NextcloudConfig:
    """Configuration snapshot for a Nextcloud deployment."""

    https_enabled: bool
    certificate_trusted: bool
    mfa_enforced: bool
    backups_enabled: bool
    backup_frequency_hours: int | None
    last_restore_verification_days: int | None
    last_update_days: int | None
    app_updates_automatic: bool
    admin_allowed_networks: Sequence[str]
    log_monitoring_enabled: bool


def audit_nextcloud(config: NextcloudConfig) -> list[CheckResult]:
    """Return security findings for a Nextcloud installation."""

    findings: list[CheckResult] = []

    if not config.https_enabled:
        findings.append(
            CheckResult(
                slug="nextcloud-https",
                message="Nextcloud should be served over HTTPS with a trusted certificate.",
                severity="high",
                remediation=(
                    "Terminate TLS with a trusted certificate via a reverse proxy or built-in SSL."
                ),
            )
        )
    elif not config.certificate_trusted:
        findings.append(
            CheckResult(
                slug="nextcloud-https",
                message="HTTPS is enabled but the certificate is not trusted by clients.",
                severity="medium",
                remediation="Install a certificate from a trusted CA or well-known internal PKI.",
            )
        )

    if not config.mfa_enforced:
        findings.append(
            CheckResult(
                slug="nextcloud-mfa",
                message="Multi-factor authentication is not enforced for all accounts.",
                severity="high",
                remediation=(
                    "Enable mandatory MFA via the security settings "
                    "and require app passwords for clients."
                ),
            )
        )

    if not config.backups_enabled:
        findings.append(
            CheckResult(
                slug="nextcloud-backups",
                message="Automated backups are disabled.",
                severity="high",
                remediation=(
                    "Schedule recurring filesystem and database backups " "to off-site storage."
                ),
            )
        )
    else:
        if config.backup_frequency_hours is None or config.backup_frequency_hours > 24:
            findings.append(
                CheckResult(
                    slug="nextcloud-backups",
                    message="Backups run infrequently. Aim for at least daily snapshots.",
                    severity="medium",
                    remediation="Adjust the backup schedule to run every 24 hours or more often.",
                )
            )
        if (
            config.last_restore_verification_days is None
            or config.last_restore_verification_days > 30
        ):
            findings.append(
                CheckResult(
                    slug="nextcloud-restore-test",
                    message="Restore procedures have not been tested in the last 30 days.",
                    severity="medium",
                    remediation="Perform routine restore drills to verify backup integrity.",
                )
            )

    if config.last_update_days is None or config.last_update_days > 30:
        findings.append(
            CheckResult(
                slug="nextcloud-updates",
                message="Nextcloud or its apps have not been updated in over 30 days.",
                severity="medium",
                remediation=(
                    "Plan a maintenance window to apply the latest core " "and app updates."
                ),
            )
        )
    elif not config.app_updates_automatic:
        findings.append(
            CheckResult(
                slug="nextcloud-updates",
                message="Automatic app updates are disabled, increasing drift risk.",
                severity="low",
                remediation=(
                    "Enable automatic app updates or schedule frequent " "manual reviews."
                ),
            )
        )

    if _is_network_list_open(config.admin_allowed_networks):
        findings.append(
            CheckResult(
                slug="nextcloud-admin-network",
                message="Admin interface is reachable from untrusted networks.",
                severity="high",
                remediation="Restrict access to VPN ranges or internal subnets only.",
            )
        )

    if not config.log_monitoring_enabled:
        findings.append(
            CheckResult(
                slug="nextcloud-log-monitoring",
                message="Logs are not actively monitored for suspicious activity.",
                severity="medium",
                remediation=(
                    "Enable log shipping or alerting to monitor " "authentication and sync events."
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


__all__ = [
    "CheckResult",
    "Severity",
    "VaultWardenConfig",
    "NextcloudConfig",
    "audit_vaultwarden",
    "audit_nextcloud",
]
