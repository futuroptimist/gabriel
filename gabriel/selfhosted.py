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
                message="Environment variable `VAULTWARDEN_ADMIN_TOKEN` or master key is weak or unset.",
                severity="high",
                remediation=(
                    "Provision a random token of at least 32 characters mixing cases, numbers, and symbols."
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
    "audit_vaultwarden",
]
