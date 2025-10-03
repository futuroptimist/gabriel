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
        return f"{labels[-2]}.{labels[-1]}"
    return hostname


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

        if known_domains:
            for known in known_domains:
                clean_known = known.lower().strip()
                if not clean_known:
                    continue
                if hostname == clean_known or hostname.endswith(f".{clean_known}"):
                    continue
                ratio = SequenceMatcher(None, registrable_domain, clean_known).ratio()
                if ratio >= 0.78 and registrable_domain != clean_known:
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
