"""Heuristics for spotting phishing indicators in URLs and text."""

from __future__ import annotations

import ipaddress
import re
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from difflib import SequenceMatcher
from functools import lru_cache
from typing import Final
from urllib.parse import parse_qsl, unquote, urlparse

from publicsuffix2 import get_sld

_SUSPICIOUS_TLDS: Final[frozenset[str]] = frozenset(
    {
        "zip",
        "review",
        "country",
        "kim",
        "cricket",
        "science",
        "work",
        "party",
        "gq",
        "ml",
        "cf",
        "tk",
        "xyz",
        "top",
        "click",
        "link",
    }
)

_URL_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"https?://[\w\-._~:/?#\[\]@!$&'()*+,;=%]+",
    flags=re.IGNORECASE,
)

_SHORTENER_DOMAINS: Final[frozenset[str]] = frozenset(
    {
        "bit.ly",
        "tinyurl.com",
        "t.co",
        "goo.gl",
        "ow.ly",
        "is.gd",
        "buff.ly",
        "rb.gy",
    }
)

_STANDARD_PORTS: Final[frozenset[int]] = frozenset({80, 443})

_SUSPICIOUS_DOWNLOAD_SEVERITY: Final[dict[str, str]] = {
    "exe": "high",
    "scr": "high",
    "bat": "high",
    "cmd": "high",
    "com": "high",
    "msi": "high",
    "msix": "high",
    "msixbundle": "high",
    "ps1": "high",
    "psm1": "high",
    "vbs": "high",
    "js": "high",
    "jse": "high",
    "jar": "high",
    "apk": "high",
    "hta": "high",
    "dll": "high",
    "pif": "high",
    "gadget": "high",
    "zip": "medium",
    "rar": "medium",
    "7z": "medium",
    "gz": "medium",
    "bz2": "medium",
    "xz": "medium",
    "tgz": "medium",
    "tar": "medium",
    "iso": "medium",
}


@dataclass(frozen=True, slots=True)
class PhishingFinding:
    """A heuristic finding describing why ``url`` may be risky."""

    url: str
    indicator: str
    message: str
    severity: str


def extract_urls(text: str) -> list[str]:
    """Return HTTP(S) URLs discovered in ``text`` in appearance order."""
    return [match.group(0) for match in _URL_PATTERN.finditer(text)]


def _iter_domain_labels(hostname: str) -> Iterator[str]:
    return (label for label in hostname.split(".") if label)


@lru_cache(maxsize=4096)
def _registrable_domain_for(hostname: str) -> str:
    """Return the registrable domain for ``hostname`` using public suffix data."""
    if not hostname:
        return ""

    registrable = get_sld(hostname)
    if registrable and "." in registrable:
        return registrable

    labels = list(_iter_domain_labels(hostname))
    if len(labels) >= 2:
        return ".".join(labels[-2:])
    if labels:
        return labels[0]
    return ""


def _split_registrable_domain(domain: str) -> tuple[str, str]:
    """Split a registrable domain into its label and suffix components."""
    if not domain:
        return "", ""

    if "." not in domain:
        return domain, ""

    label, _, suffix = domain.partition(".")
    return label, suffix


def analyze_url(url: str, known_domains: Iterable[str] | None = None) -> list[PhishingFinding]:
    """Analyse ``url`` and return heuristic phishing findings."""
    parsed = urlparse(url)
    hostname = (parsed.hostname or "").lower()
    query_params = parse_qsl(parsed.query, keep_blank_values=True)
    findings: list[PhishingFinding] = []

    if parsed.scheme == "http":
        findings.append(
            PhishingFinding(
                url=url,
                indicator="insecure-scheme",
                message="Link uses HTTP instead of HTTPS",
                severity="medium",
            )
        )

    try:
        port = parsed.port
    except ValueError:
        findings.append(
            PhishingFinding(
                url=url,
                indicator="invalid-port",
                message="Link specifies an invalid network port",
                severity="medium",
            )
        )
        port = None
    if port is not None and port not in _STANDARD_PORTS:
        findings.append(
            PhishingFinding(
                url=url,
                indicator="nonstandard-port",
                message=f"Link targets uncommon network port {port}",
                severity="medium",
            )
        )

    if parsed.username or parsed.password:
        findings.append(
            PhishingFinding(
                url=url,
                indicator="embedded-credentials",
                message="Link embeds credentials before the hostname",
                severity="high",
            )
        )

    if hostname:
        if "xn--" in hostname:
            findings.append(
                PhishingFinding(
                    url=url,
                    indicator="punycode-domain",
                    message="Domain contains punycode which is often used for homograph attacks",
                    severity="high",
                )
            )

        try:
            ipaddress.ip_address(hostname)
        except ValueError:
            pass
        else:
            findings.append(
                PhishingFinding(
                    url=url,
                    indicator="ip-address-host",
                    message="Domain is a raw IP address instead of a hostname",
                    severity="medium",
                )
            )

        labels = list(_iter_domain_labels(hostname))
        tld = labels[-1] if labels else ""
        if tld and tld in _SUSPICIOUS_TLDS:
            findings.append(
                PhishingFinding(
                    url=url,
                    indicator="suspicious-tld",
                    message=f"Top-level domain .{tld} is frequently abused for phishing",
                    severity="medium",
                )
            )

        registrable_domain = _registrable_domain_for(hostname)
        if registrable_domain and registrable_domain in _SHORTENER_DOMAINS:
            findings.append(
                PhishingFinding(
                    url=url,
                    indicator="url-shortener",
                    message=(
                        "Domain is a known URL shortener which obscures the final destination"
                    ),
                    severity="medium",
                )
            )
        registrable_label, registrable_suffix = _split_registrable_domain(registrable_domain)

        if known_domains:
            for known in known_domains:
                clean_known = known.lower().strip()
                if not clean_known:
                    continue

                normalized_known = clean_known.rstrip(".") or clean_known

                if hostname == clean_known or hostname.endswith(f".{clean_known}"):
                    continue
                if normalized_known != clean_known and (
                    hostname == normalized_known or hostname.endswith(f".{normalized_known}")
                ):
                    continue
                if normalized_known and hostname == f"{normalized_known}.":
                    continue

                if (
                    normalized_known
                    and f"{normalized_known}." in hostname
                    and not hostname.endswith(f".{normalized_known}")
                    and hostname != f"{normalized_known}."
                ):
                    findings.append(
                        PhishingFinding(
                            url=url,
                            indicator="embedded-known-domain",
                            message=(
                                "Domain nests trusted brand "
                                f"{normalized_known} under registrable domain "
                                f"{registrable_domain or hostname}"
                            ),
                            severity="high",
                        )
                    )
                    break

                known_registrable = _registrable_domain_for(clean_known)
                if known_registrable and registrable_domain != known_registrable:
                    known_label, known_suffix = _split_registrable_domain(known_registrable)
                    label_ratio = 0.0
                    if registrable_label and known_label:
                        label_ratio = SequenceMatcher(None, registrable_label, known_label).ratio()

                    base_ratio = SequenceMatcher(
                        None, registrable_domain, known_registrable
                    ).ratio()
                    shared_suffix = registrable_suffix and (registrable_suffix == known_suffix)
                    label_overlap = False
                    if shared_suffix and registrable_label and known_label:
                        label_overlap = (
                            registrable_label.startswith(known_label)
                            or registrable_label.endswith(known_label)
                            or known_label.startswith(registrable_label)
                            or known_label.endswith(registrable_label)
                        )

                    if (
                        base_ratio >= 0.78
                        or (shared_suffix and label_ratio >= 0.78)
                        or label_overlap
                    ):
                        findings.append(
                            PhishingFinding(
                                url=url,
                                indicator="lookalike-domain",
                                message=(
                                    "Domain closely resembles known brand "
                                    f"{clean_known}; verify the link before continuing"
                                ),
                                severity="high",
                            )
                        )
                        break

    suspicious_downloads_seen: set[tuple[str, str]] = set()

    def _consider_download_candidate(raw: str, location: str) -> None:
        decoded = unquote(raw)
        sanitized = decoded.strip()
        if not sanitized:
            return
        sanitized = sanitized.splitlines()[0]
        candidate = sanitized.rsplit("/", 1)[-1]
        candidate = candidate.strip().strip("\"'()[]{}<>")
        candidate = candidate.rstrip(".,;")
        if not candidate or "." not in candidate:
            return
        parts = [segment for segment in candidate.split(".") if segment]
        if len(parts) < 2:
            return
        extension = parts[-1].lower()
        severity = _SUSPICIOUS_DOWNLOAD_SEVERITY.get(extension)
        if severity is None:
            return
        normalized = candidate.lower()
        key = (normalized, extension)
        if key in suspicious_downloads_seen:
            return
        suspicious_downloads_seen.add(key)
        double_extension = len(parts) >= 3
        if double_extension:
            message = (
                f"Link references double-extension download '{candidate}' ending with .{extension}"
            )
        else:
            message = f"Link references downloadable file '{candidate}' ending with .{extension}"
        if location == "query":
            message += " via query parameter"
        elif location == "fragment":
            message += " via fragment"
        findings.append(
            PhishingFinding(
                url=url,
                indicator="suspicious-download",
                message=message,
                severity=severity,
            )
        )

    if parsed.path:
        for segment in (part for part in parsed.path.split("/") if part):
            _consider_download_candidate(segment, "path")

    for _, value in query_params:
        _consider_download_candidate(value, "query")

    if parsed.fragment:
        _consider_download_candidate(parsed.fragment, "fragment")

    if parsed.query:
        redirect_hosts: set[str] = set()
        for _, value in query_params:
            candidate = value.strip()
            if not candidate:
                continue
            redirect = urlparse(candidate)
            redirect_host = (redirect.hostname or "").lower()
            if redirect.scheme not in {"http", "https"}:
                continue
            if not redirect_host:
                continue
            if hostname and (
                redirect_host == hostname
                or redirect_host.endswith(f".{hostname}")
                or hostname.endswith(f".{redirect_host}")
            ):
                continue
            if redirect_host in redirect_hosts:
                continue
            redirect_hosts.add(redirect_host)
            findings.append(
                PhishingFinding(
                    url=url,
                    indicator="external-redirect",
                    message=(
                        "Link includes redirect parameter targeting external host "
                        f"{redirect_host}"
                    ),
                    severity="medium",
                )
            )

    return findings


def analyze_text_for_phishing(
    text: str, *, known_domains: Iterable[str] | None = None
) -> list[PhishingFinding]:
    """Analyse ``text`` and return phishing findings for embedded URLs."""
    findings: list[PhishingFinding] = []
    for url in extract_urls(text):
        findings.extend(analyze_url(url, known_domains=known_domains))
    return findings


__all__ = [
    "PhishingFinding",
    "analyze_text_for_phishing",
    "analyze_url",
    "extract_urls",
]
