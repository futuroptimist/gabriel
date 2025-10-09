# bandit:skip-file

from __future__ import annotations

from collections.abc import Iterable

import pytest

from gabriel.selfhosted import (
    CheckResult,
    NextcloudConfig,
    SyncthingConfig,
    VaultWardenConfig,
    audit_nextcloud,
    audit_syncthing,
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


def test_audit_syncthing_flags_missing_https() -> None:
    config = SyncthingConfig(
        https_enabled=False,
        global_discovery_enabled=False,
        relays_enabled=False,
        connected_device_ids=("ABC123",),
        trusted_device_ids=("ABC123",),
    )

    findings = audit_syncthing(config)

    slugs = _finding_slugs(findings)
    assert "syncthing-https" in slugs  # nosec B101
    assert any("HTTPS" in finding.message for finding in findings)  # nosec B101


def test_audit_syncthing_detects_network_services_enabled() -> None:
    config = SyncthingConfig(
        https_enabled=True,
        global_discovery_enabled=True,
        relays_enabled=True,
        connected_device_ids=("ABC123",),
        trusted_device_ids=("ABC123",),
    )

    findings = audit_syncthing(config)

    slugs = _finding_slugs(findings)
    assert {"syncthing-global-discovery", "syncthing-relays"}.issubset(slugs)  # nosec B101


def test_audit_syncthing_detects_unknown_devices() -> None:
    config = SyncthingConfig(
        https_enabled=True,
        global_discovery_enabled=False,
        relays_enabled=False,
        connected_device_ids=("abc123", "def456"),
        trusted_device_ids=("ABC123",),
    )

    findings = audit_syncthing(config)

    slugs = _finding_slugs(findings)
    assert "syncthing-unknown-devices" in slugs  # nosec B101
    assert any("DEF456" in finding.message for finding in findings)  # nosec B101


def test_audit_syncthing_warns_when_trust_list_missing() -> None:
    config = SyncthingConfig(
        https_enabled=True,
        global_discovery_enabled=False,
        relays_enabled=False,
        connected_device_ids=("abc123",),
        trusted_device_ids=(),
    )

    findings = audit_syncthing(config)

    slugs = _finding_slugs(findings)
    assert "syncthing-trust-list" in slugs  # nosec B101


def test_audit_syncthing_passes_hardened_config() -> None:
    config = SyncthingConfig(
        https_enabled=True,
        global_discovery_enabled=False,
        relays_enabled=False,
        connected_device_ids=("abc123", "   "),
        trusted_device_ids=("ABC123",),
    )

    findings = audit_syncthing(config)

    assert findings == []  # nosec B101


def test_audit_nextcloud_flags_multiple_findings() -> None:
    config = NextcloudConfig(
        https_enabled=False,
        certificate_trusted=False,
        mfa_enforced=False,
        updates_current=False,
        backups_enabled=False,
        last_backup_verification_days=None,
        admin_allowed_networks=("0.0.0.0/0",),
        log_monitoring_enabled=False,
    )

    findings = audit_nextcloud(config)

    slugs = _finding_slugs(findings)
    assert {
        "nextcloud-https",
        "nextcloud-mfa",
        "nextcloud-updates",
        "nextcloud-backups",
        "nextcloud-admin-network",
        "nextcloud-log-monitoring",
    }.issubset(
        slugs
    )  # nosec B101


def test_audit_nextcloud_warns_on_stale_backups_and_cert() -> None:
    config = NextcloudConfig(
        https_enabled=True,
        certificate_trusted=False,
        mfa_enforced=True,
        updates_current=True,
        backups_enabled=True,
        last_backup_verification_days=90,
        admin_allowed_networks=("192.168.1.0/24",),
        log_monitoring_enabled=True,
    )

    findings = audit_nextcloud(config)

    slugs = _finding_slugs(findings)
    assert "nextcloud-https" in slugs  # nosec B101
    assert "nextcloud-restore-test" in slugs  # nosec B101


def test_audit_nextcloud_passes_hardened_config() -> None:
    config = NextcloudConfig(
        https_enabled=True,
        certificate_trusted=True,
        mfa_enforced=True,
        updates_current=True,
        backups_enabled=True,
        last_backup_verification_days=7,
        admin_allowed_networks=("10.0.0.0/24", "fd00::/8"),
        log_monitoring_enabled=True,
    )

    findings = audit_nextcloud(config)

    assert findings == []  # nosec B101
