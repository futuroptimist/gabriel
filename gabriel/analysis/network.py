"""Heuristics for assessing network service exposure risk."""

from __future__ import annotations

import ipaddress
from dataclasses import dataclass
from typing import Final, Iterable

_VALID_PROTOCOLS: Final[frozenset[str]] = frozenset({"tcp", "udp"})
_VALID_EXPOSURES: Final[frozenset[str]] = frozenset({"internet", "lan", "local"})
_VALID_SEVERITIES: Final[frozenset[str]] = frozenset({"low", "medium", "high"})
_SEVERITY_ORDER: Final[dict[str, int]] = {"high": 0, "medium": 1, "low": 2}

_HIGH_RISK_PORTS: Final[dict[int, str]] = {
    23: "Telnet",
    21: "FTP",
    445: "SMB",
    3389: "RDP",
    5900: "VNC",
}

_DATABASE_PORTS: Final[dict[int, str]] = {
    1433: "Microsoft SQL Server",
    1521: "Oracle Database",
    27017: "MongoDB",
    3306: "MySQL",
    5432: "PostgreSQL",
    6379: "Redis",
}

_HTTP_PORTS: Final[frozenset[int]] = frozenset({80, 8000, 8008, 8080, 8181, 8888})
_UDP_AMPLIFICATION_PORTS: Final[dict[int, str]] = {
    123: "NTP",
    161: "SNMP",
    1900: "SSDP/UPnP",
}


@dataclass(frozen=True, slots=True)
class NetworkService:
    """Represents a network service and its exposure characteristics."""

    name: str
    port: int
    protocol: str = "tcp"
    address: str = "0.0.0.0"  # nosec B104 - default wildcard to detect overexposed bindings
    exposure: str = "internet"
    encrypted: bool = False
    authenticated: bool = True

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("name must be a non-empty string")
        if not (1 <= self.port <= 65535):
            raise ValueError("port must be between 1 and 65535")
        normalized_protocol = self.protocol.strip().lower()
        if normalized_protocol not in _VALID_PROTOCOLS:
            raise ValueError(
                "protocol must be one of 'tcp' or 'udp'"
            )
        normalized_exposure = self.exposure.strip().lower()
        if normalized_exposure not in _VALID_EXPOSURES:
            raise ValueError(
                "exposure must be one of 'internet', 'lan', or 'local'"
            )
        address = (
            self.address.strip()
            if self.address
            else "0.0.0.0"  # nosec B104 - treat empty as wildcard for heuristics
        )

        object.__setattr__(self, "name", self.name.strip())
        object.__setattr__(self, "protocol", normalized_protocol)
        object.__setattr__(self, "exposure", normalized_exposure)
        object.__setattr__(self, "address", address)


@dataclass(frozen=True, slots=True)
class NetworkExposureFinding:
    """Represents a heuristic finding about a service exposure."""

    service: str
    port: int
    protocol: str
    exposure: str
    indicator: str
    severity: str
    message: str

    def __post_init__(self) -> None:
        if not self.service or not self.service.strip():
            raise ValueError("service must be a non-empty string")
        if self.port <= 0:
            raise ValueError("port must be a positive integer")
        if self.protocol not in _VALID_PROTOCOLS:
            raise ValueError("protocol must be one of 'tcp' or 'udp'")
        if self.exposure not in _VALID_EXPOSURES:
            raise ValueError("exposure must be one of 'internet', 'lan', or 'local'")
        if not self.indicator or not self.indicator.strip():
            raise ValueError("indicator must be a non-empty string")
        normalized_severity = self.severity.lower().strip()
        if normalized_severity not in _VALID_SEVERITIES:
            raise ValueError("severity must be 'low', 'medium', or 'high'")
        object.__setattr__(self, "severity", normalized_severity)


def analyze_network_services(services: Iterable[NetworkService]) -> list[NetworkExposureFinding]:
    """Return heuristic findings describing risky service exposures."""

    findings: list[NetworkExposureFinding] = []
    seen: set[tuple[str, str, int]] = set()

    for service in services:
        _evaluate_binding_scope(service, findings, seen)
        if service.exposure == "internet":
            _evaluate_internet_exposure(service, findings, seen)
        elif service.exposure == "lan":
            _evaluate_lan_exposure(service, findings, seen)

    findings.sort(key=lambda finding: (
        _SEVERITY_ORDER[finding.severity],
        finding.service.lower(),
        finding.port,
        finding.indicator,
    ))
    return findings


def _evaluate_binding_scope(
    service: NetworkService,
    findings: list[NetworkExposureFinding],
    seen: set[tuple[str, str, int]],
) -> None:
    address = service.address.lower()
    if _is_wildcard_address(address):
        if service.exposure == "local":
            _record_finding(
                findings,
                seen,
                service,
                indicator="wildcard-exposure",
                severity="high",
                message=(
                    f"{service.name} binds to wildcard address {service.address} despite being"
                    " marked as local-only; restrict the listener to loopback."
                ),
            )
        elif service.exposure == "lan":
            _record_finding(
                findings,
                seen,
                service,
                indicator="wildcard-exposure",
                severity="medium",
                message=(
                    f"{service.name} binds to wildcard address {service.address}; confirm"
                    " firewall rules block untrusted networks."
                ),
            )
    elif service.exposure != "internet" and _is_public_address(address):
        severity = "high" if service.exposure == "local" else "medium"
        _record_finding(
            findings,
            seen,
            service,
            indicator="public-address",
            severity=severity,
            message=(
                f"{service.name} listens on public address {service.address}"
                " while scoped to a non-internet exposure; verify segmentation."
            ),
        )


def _evaluate_internet_exposure(
    service: NetworkService,
    findings: list[NetworkExposureFinding],
    seen: set[tuple[str, str, int]],
) -> None:
    if service.port in _HIGH_RISK_PORTS:
        label = _HIGH_RISK_PORTS[service.port]
        _record_finding(
            findings,
            seen,
            service,
            indicator="high-risk-port",
            severity="high",
            message=(
                f"{service.name or label} exposes {label} to the internet; disable or tunnel the service."
            ),
        )

    if not service.authenticated:
        _record_finding(
            findings,
            seen,
            service,
            indicator="unauthenticated-service",
            severity="high",
            message=(
                f"{service.name} is reachable from the internet without authentication;"
                " enforce strong access controls."
            ),
        )

    if not service.encrypted and _looks_like_http(service):
        _record_finding(
            findings,
            seen,
            service,
            indicator="unencrypted-http",
            severity="medium",
            message=(
                f"{service.name} serves HTTP without TLS on port {service.port};"
                " terminate TLS before exposing it publicly."
            ),
        )

    if not service.encrypted and _looks_like_database(service):
        label = _DATABASE_PORTS.get(service.port, service.name)
        _record_finding(
            findings,
            seen,
            service,
            indicator="internet-database",
            severity="high",
            message=(
                f"Database service {label} is internet-accessible without transport encryption;"
                " restrict access to trusted networks."
            ),
        )

    if service.protocol == "udp" and service.port in _UDP_AMPLIFICATION_PORTS:
        label = _UDP_AMPLIFICATION_PORTS[service.port]
        _record_finding(
            findings,
            seen,
            service,
            indicator="udp-amplification",
            severity="medium",
            message=(
                f"{service.name or label} exposes UDP service {label} to the internet;"
                " configure rate limiting or disable it."
            ),
        )


def _evaluate_lan_exposure(
    service: NetworkService,
    findings: list[NetworkExposureFinding],
    seen: set[tuple[str, str, int]],
) -> None:
    if not service.authenticated and _looks_like_admin_interface(service):
        _record_finding(
            findings,
            seen,
            service,
            indicator="lan-admin-open",
            severity="medium",
            message=(
                f"{service.name} on port {service.port} lacks authentication on the LAN;"
                " restrict access before exposing dashboards."
            ),
        )


def _record_finding(
    findings: list[NetworkExposureFinding],
    seen: set[tuple[str, str, int]],
    service: NetworkService,
    *,
    indicator: str,
    severity: str,
    message: str,
) -> None:
    key = (service.name, indicator, service.port)
    if key in seen:
        return
    seen.add(key)
    findings.append(
        NetworkExposureFinding(
            service=service.name,
            port=service.port,
            protocol=service.protocol,
            exposure=service.exposure,
            indicator=indicator,
            severity=severity,
            message=message,
        )
    )


def _looks_like_http(service: NetworkService) -> bool:
    name = service.name.lower()
    return service.port in _HTTP_PORTS or "http" in name or "web" in name


def _looks_like_database(service: NetworkService) -> bool:
    if service.port in _DATABASE_PORTS:
        return True
    lowered = service.name.lower()
    return any(token in lowered for token in ("db", "database", "sql"))


def _looks_like_admin_interface(service: NetworkService) -> bool:
    lowered = service.name.lower()
    return any(keyword in lowered for keyword in ("admin", "dashboard", "grafana", "metrics"))


def _is_wildcard_address(address: str) -> bool:
    if address in {"", "*", "0.0.0.0", "::"}:  # nosec B104 - intentional wildcard check
        return True
    try:
        parsed = ipaddress.ip_address(address)
    except ValueError:
        return False
    return parsed.is_unspecified


def _is_public_address(address: str) -> bool:
    try:
        parsed = ipaddress.ip_address(address)
    except ValueError:
        return False
    return parsed.is_global


__all__ = [
    "NetworkExposureFinding",
    "NetworkService",
    "analyze_network_services",
]
