"""Tests for the egress control policy."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from gabriel.security.policies.egress_control import (
    EgressControlPolicy,
    EgressPolicyViolation,
)


def _write_allowlist(
    path: Path, *, domains: list[str] | None = None, ips: list[str] | None = None
) -> None:
    payload = {"domains": domains or [], "ips": ips or []}
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_blocks_unapproved_domain(tmp_path: Path) -> None:
    allowlist_path = tmp_path / "allowlist.json"
    _write_allowlist(allowlist_path, domains=["trusted.example"])
    policy = EgressControlPolicy(allowlist_path=allowlist_path, safe_mode=True)

    with pytest.raises(EgressPolicyViolation):
        policy.validate_request("https://evil.example")


def test_allows_allowlisted_domain_and_subdomain(tmp_path: Path) -> None:
    allowlist_path = tmp_path / "allowlist.json"
    _write_allowlist(allowlist_path, domains=["trusted.example"])
    policy = EgressControlPolicy(allowlist_path=allowlist_path, safe_mode=True)

    policy.validate_request("https://trusted.example/api")
    policy.validate_request("https://api.trusted.example/v1")


def test_updates_allowlist_on_reload(tmp_path: Path) -> None:
    allowlist_path = tmp_path / "allowlist.json"
    _write_allowlist(allowlist_path, domains=["trusted.example"])
    policy = EgressControlPolicy(allowlist_path=allowlist_path, safe_mode=True)

    with pytest.raises(EgressPolicyViolation):
        policy.validate_request("https://new.example")

    _write_allowlist(allowlist_path, domains=["trusted.example", "new.example"])
    policy.reload()

    policy.validate_request("https://new.example")


def test_prompt_injection_payload_cannot_override_allowlist(tmp_path: Path) -> None:
    allowlist_path = tmp_path / "allowlist.json"
    _write_allowlist(allowlist_path, domains=["trusted.example"])
    policy = EgressControlPolicy(allowlist_path=allowlist_path, safe_mode=True)

    payload_url = "https://evil.example/?prompt=ALLOWLIST=*"
    with pytest.raises(EgressPolicyViolation):
        policy.validate_request(payload_url)


def test_ip_allowlisting(tmp_path: Path) -> None:
    allowlist_path = tmp_path / "allowlist.json"
    _write_allowlist(allowlist_path, ips=["192.168.1.10"])
    policy = EgressControlPolicy(allowlist_path=allowlist_path, safe_mode=True)

    policy.validate_request("https://192.168.1.10/service")
    with pytest.raises(EgressPolicyViolation):
        policy.validate_request("https://192.168.1.11/service")


def test_safe_mode_blocks_without_allowlist(tmp_path: Path) -> None:
    allowlist_path = tmp_path / "allowlist.json"
    _write_allowlist(allowlist_path)
    policy = EgressControlPolicy(allowlist_path=allowlist_path, safe_mode=True)

    with pytest.raises(EgressPolicyViolation):
        policy.validate_request("https://trusted.example")


def test_safe_mode_disabled_allows_unlisted_host(tmp_path: Path) -> None:
    allowlist_path = tmp_path / "allowlist.json"
    _write_allowlist(allowlist_path)
    policy = EgressControlPolicy(allowlist_path=allowlist_path, safe_mode=False)

    policy.validate_request("https://unlisted.example")


def test_from_env_uses_environment_configuration(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    allowlist_path = tmp_path / "custom.json"
    _write_allowlist(allowlist_path, domains=["trusted.example"])
    monkeypatch.setenv("EGRESS_ALLOWLIST_PATH", str(allowlist_path))
    monkeypatch.setenv("SAFE_MODE", "false")

    policy = EgressControlPolicy.from_env()
    assert policy.safe_mode is False
    policy.validate_request("https://trusted.example")


def test_missing_allowlist_file_raises(tmp_path: Path) -> None:
    missing = tmp_path / "missing.json"
    with pytest.raises(RuntimeError):
        EgressControlPolicy(allowlist_path=missing, safe_mode=True)


def test_invalid_allowlist_structure_raises(tmp_path: Path) -> None:
    allowlist_path = tmp_path / "allowlist.json"
    allowlist_path.write_text("[]", encoding="utf-8")
    with pytest.raises(RuntimeError):
        EgressControlPolicy(allowlist_path=allowlist_path, safe_mode=True)


def test_non_string_entries_rejected(tmp_path: Path) -> None:
    allowlist_path = tmp_path / "allowlist.json"
    payload = json.dumps({"domains": [123], "ips": ["10.0.0.1"]})
    allowlist_path.write_text(payload, encoding="utf-8")
    with pytest.raises(RuntimeError):
        EgressControlPolicy(allowlist_path=allowlist_path, safe_mode=True)


def test_validate_rejects_missing_host(tmp_path: Path) -> None:
    allowlist_path = tmp_path / "allowlist.json"
    _write_allowlist(allowlist_path, domains=["trusted.example"])
    policy = EgressControlPolicy(allowlist_path=allowlist_path, safe_mode=True)

    with pytest.raises(EgressPolicyViolation):
        policy.validate_request("https:///resource")


def test_validate_rejects_invalid_scheme(tmp_path: Path) -> None:
    allowlist_path = tmp_path / "allowlist.json"
    _write_allowlist(allowlist_path, domains=["trusted.example"])
    policy = EgressControlPolicy(allowlist_path=allowlist_path, safe_mode=True)

    with pytest.raises(EgressPolicyViolation):
        policy.validate_request("ftp://trusted.example/resource")
