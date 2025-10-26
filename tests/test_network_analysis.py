"""Tests for the network exposure heuristics."""

from __future__ import annotations

import pytest

from gabriel.analysis.network import (
    NetworkExposureFinding,
    NetworkService,
    analyze_network_services,
)


def _finding_by_indicator(findings: list[NetworkExposureFinding], indicator: str) -> NetworkExposureFinding:
    for finding in findings:
        if finding.indicator == indicator:
            return finding
    raise AssertionError(f"Indicator {indicator!r} not found. Findings: {findings}")


def test_internet_exposed_high_risk_port_flags_high_severity() -> None:
    service = NetworkService(name="RDP", port=3389, exposure="internet")

    findings = analyze_network_services([service])

    finding = _finding_by_indicator(findings, "high-risk-port")
    assert finding.severity == "high"
    assert "RDP" in finding.message


def test_unencrypted_http_service_warns() -> None:
    service = NetworkService(
        name="Status Page",
        port=8080,
        exposure="internet",
        encrypted=False,
    )

    findings = analyze_network_services([service])

    finding = _finding_by_indicator(findings, "unencrypted-http")
    assert finding.severity == "medium"
    assert "Status Page" in finding.message


def test_database_service_is_flagged_even_with_tls() -> None:
    service = NetworkService(
        name="Analytics DB",
        port=5432,
        exposure="internet",
        encrypted=True,
    )

    findings = analyze_network_services([service])

    finding = _finding_by_indicator(findings, "internet-database")
    assert finding.severity == "high"
    assert "TLS enabled" in finding.message


def test_missing_authentication_on_public_service_is_high_severity() -> None:
    service = NetworkService(
        name="Grafana",
        port=3000,
        exposure="internet",
        authenticated=False,
    )

    findings = analyze_network_services([service])

    finding = _finding_by_indicator(findings, "unauthenticated-service")
    assert finding.severity == "high"
    assert "Grafana" in finding.message


def test_wildcard_local_binding_is_flagged() -> None:
    service = NetworkService(
        name="Dev Server",
        port=5000,
        exposure="local",
        address="0.0.0.0",
    )

    findings = analyze_network_services([service])

    finding = _finding_by_indicator(findings, "wildcard-exposure")
    assert finding.severity == "high"
    assert "0.0.0.0" in finding.message


def test_safe_localhost_service_produces_no_findings() -> None:
    service = NetworkService(
        name="Local API",
        port=5001,
        exposure="local",
        address="127.0.0.1",
        encrypted=True,
    )

    assert analyze_network_services([service]) == []


def test_results_are_sorted_by_severity_and_name() -> None:
    services = [
        NetworkService(name="Database", port=5432, exposure="internet"),
        NetworkService(name="Metrics", port=9100, exposure="internet", authenticated=False),
        NetworkService(name="Website", port=80, exposure="internet", encrypted=False),
    ]

    findings = analyze_network_services(services)

    severities = [finding.severity for finding in findings]
    assert severities == sorted(severities, key=lambda value: {"high": 0, "medium": 1, "low": 2}[value])
    assert findings[0].indicator in {"high-risk-port", "unauthenticated-service", "internet-database"}


@pytest.mark.parametrize(
    "port",
    [0, 70000],
)
def test_invalid_port_raises(port: int) -> None:
    with pytest.raises(ValueError):
        NetworkService(name="Bad", port=port)


@pytest.mark.parametrize("exposure", ["INTERNET", "Lan", "LOCAL"])
def test_exposure_is_normalised(exposure: str) -> None:
    service = NetworkService(name="ssh", port=22, exposure=exposure)

    assert service.exposure == exposure.lower()


def test_network_service_requires_name() -> None:
    with pytest.raises(ValueError):
        NetworkService(name="  ", port=22)


@pytest.mark.parametrize("protocol", ["tcp ", "UDP", "http"])
def test_network_service_invalid_protocol(protocol: str) -> None:
    if protocol.strip().lower() in {"tcp", "udp"}:
        assert NetworkService(name="svc", port=22, protocol=protocol).protocol in {"tcp", "udp"}
    else:
        with pytest.raises(ValueError):
            NetworkService(name="svc", port=22, protocol=protocol)


def test_network_service_invalid_exposure() -> None:
    with pytest.raises(ValueError):
        NetworkService(name="svc", port=22, exposure="external")


@pytest.mark.parametrize(
    "override",
    [
        {"service": ""},
        {"port": 0},
        {"protocol": "icmp"},
        {"exposure": "dmz"},
        {"indicator": ""},
        {"severity": "critical"},
    ],
)
def test_network_exposure_finding_validates_inputs(override: dict[str, object]) -> None:
    base = {
        "service": "svc",
        "port": 1,
        "protocol": "tcp",
        "exposure": "internet",
        "indicator": "demo",
        "severity": "high",
        "message": "demo",
    }
    base.update(override)
    with pytest.raises(ValueError):
        NetworkExposureFinding(**base)  # type: ignore[arg-type]


def test_lan_admin_interface_without_authentication_is_flagged() -> None:
    service = NetworkService(
        name="Metrics Dashboard",
        port=9100,
        exposure="lan",
        authenticated=False,
    )

    findings = analyze_network_services([service])

    finding = _finding_by_indicator(findings, "lan-admin-open")
    assert finding.severity == "medium"


def test_public_address_in_lan_scope_triggers_warning() -> None:
    service = NetworkService(
        name="LAN SSH",
        port=22,
        exposure="lan",
        address="8.8.8.8",
    )

    findings = analyze_network_services([service])

    finding = _finding_by_indicator(findings, "public-address")
    assert finding.severity == "medium"


def test_udp_amplification_service_is_detected() -> None:
    service = NetworkService(
        name="SSDP",
        port=1900,
        protocol="udp",
        exposure="internet",
    )

    findings = analyze_network_services([service])

    finding = _finding_by_indicator(findings, "udp-amplification")
    assert finding.severity == "medium"


def test_duplicate_services_do_not_duplicate_findings() -> None:
    service = NetworkService(name="RDP", port=3389, exposure="internet")

    findings = analyze_network_services([service, service])

    assert len(findings) == 1


def test_domain_address_does_not_raise_and_returns_no_findings() -> None:
    service = NetworkService(
        name="Local host", port=9001, exposure="local", address="myservice.internal"
    )

    assert analyze_network_services([service]) == []
