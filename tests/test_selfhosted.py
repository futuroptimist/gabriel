# bandit:skip-file

from __future__ import annotations

from collections.abc import Iterable

import pytest

from gabriel.selfhosted import (
    CheckResult,
    PhotoPrismConfig,
    VaultWardenConfig,
    audit_photoprism,
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


def test_audit_photoprism_flags_https_and_admin_controls() -> None:
    config = PhotoPrismConfig(
        https_enabled=False,
        admin_password=("weakpass"),  # pragma: allowlist secret  # nosec B106
        library_outside_container=False,
        library_permissions_strict=False,
        backups_enabled=True,
        backup_frequency_hours=24,
        backup_location_hardened=True,
        unreviewed_plugins=(),
    )

    findings = audit_photoprism(config)

    slugs = _finding_slugs(findings)
    assert "photoprism-https" in slugs  # nosec B101 - pytest assertion
    assert "photoprism-admin-password" in slugs  # nosec B101
    assert "photoprism-library-location" in slugs  # nosec B101
    assert "photoprism-library-permissions" in slugs  # nosec B101


def test_audit_photoprism_flags_backup_gaps_and_plugin_review() -> None:
    config = PhotoPrismConfig(
        https_enabled=True,
        admin_password=("Password1"),  # pragma: allowlist secret  # nosec B106
        library_outside_container=True,
        library_permissions_strict=True,
        backups_enabled=True,
        backup_frequency_hours=72,
        backup_location_hardened=False,
        unreviewed_plugins=("third-party-theme",),
    )

    findings = audit_photoprism(config)

    slugs = _finding_slugs(findings)
    assert "photoprism-admin-password" in slugs  # nosec B101
    assert "photoprism-backups" in slugs  # nosec B101
    assert "photoprism-backup-location" in slugs  # nosec B101
    assert "photoprism-plugins" in slugs  # nosec B101


def test_audit_photoprism_detects_missing_password_and_backups_disabled() -> None:
    config = PhotoPrismConfig(
        https_enabled=True,
        admin_password=None,
        library_outside_container=True,
        library_permissions_strict=True,
        backups_enabled=False,
        backup_frequency_hours=None,
        backup_location_hardened=True,
        unreviewed_plugins=(),
    )

    findings = audit_photoprism(config)

    slugs = _finding_slugs(findings)
    assert "photoprism-admin-password" in slugs  # nosec B101
    assert "photoprism-backups" in slugs  # nosec B101


def test_audit_photoprism_passes_hardened_config() -> None:
    config = PhotoPrismConfig(
        https_enabled=True,
        admin_password=("Adm1nPassw0rd!"),  # pragma: allowlist secret  # nosec B106
        library_outside_container=True,
        library_permissions_strict=True,
        backups_enabled=True,
        backup_frequency_hours=12,
        backup_location_hardened=True,
        unreviewed_plugins=(),
    )

    findings = audit_photoprism(config)

    assert findings == []  # nosec B101
