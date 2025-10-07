# bandit:skip-file

from __future__ import annotations

from collections.abc import Iterable

import pytest

from gabriel.selfhosted import (
    CheckResult,
    NextcloudConfig,
    VaultWardenConfig,
    audit_nextcloud,
    audit_vaultwarden,
)


def _finding_slugs(findings: Iterable[CheckResult]) -> set[str]:
    return {finding.slug for finding in findings}


def test_audit_vaultwarden_flags_missing_https() -> None:
    config = VaultWardenConfig(
        https_enabled=False,
        certificate_trusted=False,
        encryption_key="hunter2",
        backup_enabled=True,
        backup_frequency_hours=24,
        last_restore_verification_days=7,
        admin_interface_enabled=True,
        admin_allowed_networks=("192.168.10.0/24",),
    )

    findings = audit_vaultwarden(config)

    slugs = _finding_slugs(findings)
    assert "vaultwarden-https" in slugs  # nosec B101 - pytest assertion
    assert any("HTTPS" in finding.message for finding in findings)  # nosec B101


def test_audit_vaultwarden_detects_weak_encryption_key() -> None:
    config = VaultWardenConfig(
        https_enabled=True,
        certificate_trusted=True,
        encryption_key="short",  # too short
        backup_enabled=True,
        backup_frequency_hours=12,
        last_restore_verification_days=10,
        admin_interface_enabled=True,
        admin_allowed_networks=("10.0.0.0/8",),
    )

    findings = audit_vaultwarden(config)

    slugs = _finding_slugs(findings)
    assert "vaultwarden-encryption-key" in slugs  # nosec B101


def test_audit_vaultwarden_detects_missing_encryption_key() -> None:
    config = VaultWardenConfig(
        https_enabled=True,
        certificate_trusted=True,
        encryption_key=None,
        backup_enabled=True,
        backup_frequency_hours=12,
        last_restore_verification_days=10,
        admin_interface_enabled=True,
        admin_allowed_networks=("10.0.0.0/8",),
    )

    findings = audit_vaultwarden(config)

    slugs = _finding_slugs(findings)
    assert "vaultwarden-encryption-key" in slugs  # nosec B101


def test_audit_vaultwarden_warns_on_open_admin_networks() -> None:
    config = VaultWardenConfig(
        https_enabled=True,
        certificate_trusted=True,
        encryption_key="b" * 40 + "1!",
        backup_enabled=True,
        backup_frequency_hours=24,
        last_restore_verification_days=5,
        admin_interface_enabled=True,
        admin_allowed_networks=("0.0.0.0/0", "::/0"),
    )

    findings = audit_vaultwarden(config)

    slugs = _finding_slugs(findings)
    assert "vaultwarden-admin-network" in slugs  # nosec B101


def test_audit_vaultwarden_warns_on_untrusted_certificate() -> None:
    config = VaultWardenConfig(
        https_enabled=True,
        certificate_trusted=False,
        encryption_key="b" * 30 + "Aa1!",
        backup_enabled=True,
        backup_frequency_hours=24,
        last_restore_verification_days=5,
        admin_interface_enabled=True,
        admin_allowed_networks=("192.168.10.0/24",),
    )

    findings = audit_vaultwarden(config)

    slugs = _finding_slugs(findings)
    assert "vaultwarden-https" in slugs  # nosec B101


def test_audit_vaultwarden_warns_when_backups_disabled() -> None:
    config = VaultWardenConfig(
        https_enabled=True,
        certificate_trusted=True,
        encryption_key="b" * 30 + "Aa1!",
        backup_enabled=False,
        backup_frequency_hours=None,
        last_restore_verification_days=None,
        admin_interface_enabled=True,
        admin_allowed_networks=("192.168.10.0/24",),
    )

    findings = audit_vaultwarden(config)

    slugs = _finding_slugs(findings)
    assert "vaultwarden-backups" in slugs  # nosec B101


def test_audit_vaultwarden_warns_on_backup_cadence_and_restore() -> None:
    config = VaultWardenConfig(
        https_enabled=True,
        certificate_trusted=True,
        encryption_key="b" * 30 + "Aa1!",
        backup_enabled=True,
        backup_frequency_hours=72,
        last_restore_verification_days=45,
        admin_interface_enabled=True,
        admin_allowed_networks=("192.168.10.0/24",),
    )

    findings = audit_vaultwarden(config)

    slugs = _finding_slugs(findings)
    assert "vaultwarden-backups" in slugs  # nosec B101
    assert "vaultwarden-restore-test" in slugs  # nosec B101


def test_audit_vaultwarden_warns_when_admin_network_list_empty() -> None:
    config = VaultWardenConfig(
        https_enabled=True,
        certificate_trusted=True,
        encryption_key="b" * 30 + "Aa1!",
        backup_enabled=True,
        backup_frequency_hours=12,
        last_restore_verification_days=10,
        admin_interface_enabled=True,
        admin_allowed_networks=("", "   "),
    )

    findings = audit_vaultwarden(config)

    slugs = _finding_slugs(findings)
    assert "vaultwarden-admin-network" in slugs  # nosec B101


def test_audit_vaultwarden_skips_admin_checks_when_disabled() -> None:
    config = VaultWardenConfig(
        https_enabled=True,
        certificate_trusted=True,
        encryption_key="b" * 30 + "Aa1!",
        backup_enabled=True,
        backup_frequency_hours=12,
        last_restore_verification_days=10,
        admin_interface_enabled=False,
        admin_allowed_networks=("0.0.0.0/0",),
    )

    findings = audit_vaultwarden(config)

    slugs = _finding_slugs(findings)
    assert "vaultwarden-admin-network" not in slugs  # nosec B101


@pytest.mark.parametrize(
    "key",
    [
        "Aa1!" + "b" * 28,
        "CorrectHorseBatteryStaple123!CorrectHorseBatteryStaple",
    ],
)
def test_audit_vaultwarden_passes_hardened_config(key: str) -> None:
    config = VaultWardenConfig(
        https_enabled=True,
        certificate_trusted=True,
        encryption_key=key,
        backup_enabled=True,
        backup_frequency_hours=12,
        last_restore_verification_days=7,
        admin_interface_enabled=True,
        admin_allowed_networks=("192.168.10.0/24", "10.0.0.0/16"),
    )

    findings = audit_vaultwarden(config)

    assert findings == []  # nosec B101


def test_audit_nextcloud_flags_missing_https() -> None:
    config = NextcloudConfig(
        https_enabled=False,
        certificate_trusted=False,
        mfa_enforced=True,
        backups_enabled=True,
        backup_frequency_hours=12,
        last_restore_verification_days=7,
        last_update_days=10,
        app_updates_automatic=True,
        admin_allowed_networks=("192.168.10.0/24",),
        log_monitoring_enabled=True,
    )

    findings = audit_nextcloud(config)

    slugs = _finding_slugs(findings)
    assert "nextcloud-https" in slugs  # nosec B101


def test_audit_nextcloud_detects_missing_mfa() -> None:
    config = NextcloudConfig(
        https_enabled=True,
        certificate_trusted=True,
        mfa_enforced=False,
        backups_enabled=True,
        backup_frequency_hours=12,
        last_restore_verification_days=7,
        last_update_days=10,
        app_updates_automatic=True,
        admin_allowed_networks=("192.168.10.0/24",),
        log_monitoring_enabled=True,
    )

    findings = audit_nextcloud(config)

    slugs = _finding_slugs(findings)
    assert "nextcloud-mfa" in slugs  # nosec B101


def test_audit_nextcloud_warns_on_backup_and_restore_gaps() -> None:
    config = NextcloudConfig(
        https_enabled=True,
        certificate_trusted=True,
        mfa_enforced=True,
        backups_enabled=True,
        backup_frequency_hours=48,
        last_restore_verification_days=90,
        last_update_days=5,
        app_updates_automatic=True,
        admin_allowed_networks=("192.168.10.0/24",),
        log_monitoring_enabled=True,
    )

    findings = audit_nextcloud(config)

    slugs = _finding_slugs(findings)
    assert "nextcloud-backups" in slugs  # nosec B101
    assert "nextcloud-restore-test" in slugs  # nosec B101


def test_audit_nextcloud_warns_when_backups_disabled() -> None:
    config = NextcloudConfig(
        https_enabled=True,
        certificate_trusted=True,
        mfa_enforced=True,
        backups_enabled=False,
        backup_frequency_hours=None,
        last_restore_verification_days=None,
        last_update_days=5,
        app_updates_automatic=True,
        admin_allowed_networks=("192.168.10.0/24",),
        log_monitoring_enabled=True,
    )

    findings = audit_nextcloud(config)

    slugs = _finding_slugs(findings)
    assert "nextcloud-backups" in slugs  # nosec B101


def test_audit_nextcloud_warns_when_backup_frequency_unknown() -> None:
    config = NextcloudConfig(
        https_enabled=True,
        certificate_trusted=True,
        mfa_enforced=True,
        backups_enabled=True,
        backup_frequency_hours=None,
        last_restore_verification_days=7,
        last_update_days=5,
        app_updates_automatic=True,
        admin_allowed_networks=("192.168.10.0/24",),
        log_monitoring_enabled=True,
    )

    findings = audit_nextcloud(config)

    slugs = _finding_slugs(findings)
    assert "nextcloud-backups" in slugs  # nosec B101


def test_audit_nextcloud_warns_on_stale_updates_and_app_reviews() -> None:
    config = NextcloudConfig(
        https_enabled=True,
        certificate_trusted=True,
        mfa_enforced=True,
        backups_enabled=True,
        backup_frequency_hours=12,
        last_restore_verification_days=7,
        last_update_days=45,
        app_updates_automatic=False,
        admin_allowed_networks=("192.168.10.0/24",),
        log_monitoring_enabled=True,
    )

    findings = audit_nextcloud(config)

    slugs = _finding_slugs(findings)
    assert "nextcloud-updates" in slugs  # nosec B101
    assert any(
        "not been updated" in finding.message.lower()
        for finding in findings
        if finding.slug == "nextcloud-updates"
    )  # nosec B101


def test_audit_nextcloud_warns_on_open_admin_network_and_logging() -> None:
    config = NextcloudConfig(
        https_enabled=True,
        certificate_trusted=True,
        mfa_enforced=True,
        backups_enabled=True,
        backup_frequency_hours=12,
        last_restore_verification_days=7,
        last_update_days=10,
        app_updates_automatic=True,
        admin_allowed_networks=("0.0.0.0/0",),
        log_monitoring_enabled=False,
    )

    findings = audit_nextcloud(config)

    slugs = _finding_slugs(findings)
    assert "nextcloud-admin-network" in slugs  # nosec B101
    assert "nextcloud-log-monitoring" in slugs  # nosec B101


def test_audit_nextcloud_passes_hardened_config() -> None:
    config = NextcloudConfig(
        https_enabled=True,
        certificate_trusted=True,
        mfa_enforced=True,
        backups_enabled=True,
        backup_frequency_hours=12,
        last_restore_verification_days=7,
        last_update_days=7,
        app_updates_automatic=True,
        admin_allowed_networks=("192.168.10.0/24", "10.0.0.0/16"),
        log_monitoring_enabled=True,
    )

    findings = audit_nextcloud(config)

    assert findings == []  # nosec B101


def test_audit_nextcloud_warns_on_untrusted_certificate() -> None:
    config = NextcloudConfig(
        https_enabled=True,
        certificate_trusted=False,
        mfa_enforced=True,
        backups_enabled=True,
        backup_frequency_hours=12,
        last_restore_verification_days=7,
        last_update_days=7,
        app_updates_automatic=True,
        admin_allowed_networks=("192.168.10.0/24",),
        log_monitoring_enabled=True,
    )

    findings = audit_nextcloud(config)

    slugs = _finding_slugs(findings)
    assert "nextcloud-https" in slugs  # nosec B101
    assert any(finding.severity == "medium" for finding in findings)  # nosec B101


def test_audit_nextcloud_warns_when_updates_recent_but_automation_disabled() -> None:
    config = NextcloudConfig(
        https_enabled=True,
        certificate_trusted=True,
        mfa_enforced=True,
        backups_enabled=True,
        backup_frequency_hours=12,
        last_restore_verification_days=7,
        last_update_days=5,
        app_updates_automatic=False,
        admin_allowed_networks=("192.168.10.0/24",),
        log_monitoring_enabled=True,
    )

    findings = audit_nextcloud(config)

    slugs = _finding_slugs(findings)
    assert "nextcloud-updates" in slugs  # nosec B101
    assert any(
        finding.severity == "low" and "automatic" in finding.message.lower()
        for finding in findings
        if finding.slug == "nextcloud-updates"
    )  # nosec B101
