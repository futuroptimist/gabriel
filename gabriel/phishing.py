"""Heuristics for spotting potentially malicious hyperlinks."""

from __future__ import annotations

import ipaddress
import re
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from difflib import SequenceMatcher
from functools import lru_cache
from typing import Final
from urllib.parse import urlparse

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

_KNOWN_DOMAIN_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)(?:\.(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?))*"
)


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


def _normalize_known_domain(domain: str) -> str:
    """Return a normalised representation of a known legitimate domain."""

    cleaned = domain.lower().strip().rstrip(".")
    if not cleaned:
        return ""

    parsed = urlparse(cleaned if "://" in cleaned else f"//{cleaned}")
    hostname = (parsed.hostname or "").rstrip(".")
    if not hostname:
        return ""

    match = _KNOWN_DOMAIN_PATTERN.fullmatch(hostname)
    if not match:
        return ""

    return match.group(0)


def _contains_deceptive_subdomain(hostname: str, known_domain: str) -> bool:
    """Return ``True`` when ``hostname`` embeds ``known_domain`` before another suffix."""

    if not known_domain:
        return False

    if hostname.rstrip(".") == known_domain:
        return False

    token = f"{known_domain}."
    start = hostname.find(token)
    while start != -1:
        if start == 0 or hostname[start - 1] == ".":
            return True
        start = hostname.find(token, start + 1)
    return False


def analyze_url(url: str, known_domains: Iterable[str] | None = None) -> list[PhishingFinding]:
    """Analyse ``url`` and return heuristic phishing findings."""

    parsed = urlparse(url)
    hostname = (parsed.hostname or "").lower()
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
        registrable_label, registrable_suffix = _split_registrable_domain(registrable_domain)

        if known_domains:
            for known in known_domains:
                clean_known = _normalize_known_domain(known)
                if not clean_known:
                    continue
                if hostname == clean_known or hostname.endswith(f".{clean_known}"):
                    continue
                if _contains_deceptive_subdomain(hostname, clean_known):
                    findings.append(
                        PhishingFinding(
                            url=url,
                            indicator="deceptive-subdomain",
                            message=(
                                "Hostname embeds trusted domain "
                                f"{clean_known!r} within a different parent domain"
                            ),
                            severity="high",
                        )
                    )
                known_registrable = _registrable_domain_for(clean_known)
                if registrable_domain == known_registrable:
                    continue

                known_label, known_suffix = _split_registrable_domain(known_registrable)
                label_ratio = 0.0
                if registrable_label and known_label:
                    label_ratio = SequenceMatcher(None, registrable_label, known_label).ratio()

                base_ratio = SequenceMatcher(None, registrable_domain, known_registrable).ratio()
                shared_suffix = registrable_suffix and (registrable_suffix == known_suffix)
                label_overlap = False
                if shared_suffix and registrable_label and known_label:
                    label_overlap = (
                        registrable_label.startswith(known_label)
                        or registrable_label.endswith(known_label)
                        or known_label.startswith(registrable_label)
                        or known_label.endswith(registrable_label)
                    )

                if base_ratio >= 0.78 or (shared_suffix and label_ratio >= 0.78) or label_overlap:
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
