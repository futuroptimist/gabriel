# bandit:skip-file

from __future__ import annotations

import pytest

from gabriel.phishing import (
    PhishingFinding,
    _contains_deceptive_subdomain,
    _normalize_known_domain,
    _registrable_domain_for,
    _split_registrable_domain,
    analyze_text_for_phishing,
    analyze_url,
    extract_urls,
)


@pytest.mark.parametrize(
    "text, expected",
    [
        (
            "Check https://example.com and http://sub.domain.test/path?query=yes",
            [
                "https://example.com",
                "http://sub.domain.test/path?query=yes",
            ],
        ),
        (
            "Mixed case HTTPS://Example.COM is normalised when parsed.",
            ["HTTPS://Example.COM"],
        ),
    ],
)
def test_extract_urls(text: str, expected: list[str]) -> None:
    assert extract_urls(text) == expected  # nosec B101


def _indicator_set(findings: list[PhishingFinding]) -> set[str]:
    return {finding.indicator for finding in findings}


def test_contains_deceptive_subdomain_empty_known_returns_false() -> None:
    assert not _contains_deceptive_subdomain("example.com", "")  # nosec B101


def test_normalize_known_domain_strips_whitespace_and_dots() -> None:
    assert _normalize_known_domain(" Example.COM. ") == "example.com"  # nosec B101


def test_normalize_known_domain_rejects_malformed_hostname() -> None:
    assert _normalize_known_domain(" example.com<script>") == ""  # nosec B101


def test_normalize_known_domain_extracts_hostname_from_url() -> None:
    assert _normalize_known_domain("https://Example.com/login") == "example.com"  # nosec B101


def test_normalize_known_domain_handles_missing_hostname() -> None:
    assert _normalize_known_domain("//@") == ""  # nosec B101


def test_analyze_url_detects_multiple_indicators() -> None:
    url = "http://user:pass@xn--phish-cta.com/login"  # pragma: allowlist secret
    findings = analyze_url(url, known_domains=["phish.com"])
    indicators = _indicator_set(findings)
    assert indicators >= {  # nosec B101
        "insecure-scheme",
        "embedded-credentials",
        "punycode-domain",
    }
    assert all(f.url == url for f in findings)  # nosec B101


def test_analyze_url_flags_ip_hosts_and_suspicious_tlds() -> None:
    url = "http://192.168.1.50.example.zip"
    findings = analyze_url(url)
    indicators = _indicator_set(findings)
    assert "insecure-scheme" in indicators  # nosec B101
    assert "suspicious-tld" in indicators  # nosec B101
    assert (
        "ip-address-host" not in indicators
    )  # hostname contains dots but is not raw IP  # nosec B101


def test_analyze_url_flags_exact_ip_address() -> None:
    url = "http://192.168.1.50/login"
    findings = analyze_url(url)
    indicators = _indicator_set(findings)
    assert {"insecure-scheme", "ip-address-host"} <= indicators  # nosec B101


def test_analyze_url_detects_lookalike_domains() -> None:
    url = "https://accounts.examp1e.com"
    findings = analyze_url(url, known_domains=["example.com"])
    indicators = _indicator_set(findings)
    assert "lookalike-domain" in indicators  # nosec B101
    [finding] = [f for f in findings if f.indicator == "lookalike-domain"]
    assert finding.severity == "high"  # nosec B101


def test_analyze_url_detects_lookalike_domains_with_multi_label_suffix() -> None:
    url = "https://accounts.examp1e.co.uk"
    findings = analyze_url(url, known_domains=["example.co.uk"])
    indicators = _indicator_set(findings)
    assert "lookalike-domain" in indicators  # nosec B101


def test_analyze_url_detects_suffix_preserving_brand_injection() -> None:
    url = "https://bank-secure.co.uk"
    findings = analyze_url(url, known_domains=["bank.co.uk"])
    indicators = _indicator_set(findings)
    assert "lookalike-domain" in indicators  # nosec B101


def test_analyze_url_detects_deceptive_subdomain_injection() -> None:
    url = "https://example.com.security-check.net/login"
    findings = analyze_url(url, known_domains=["example.com"])
    indicators = _indicator_set(findings)
    assert "deceptive-subdomain" in indicators  # nosec B101
    [finding] = [f for f in findings if f.indicator == "deceptive-subdomain"]
    assert finding.severity == "high"  # nosec B101
    expected_message = (
        "Hostname embeds trusted domain "
        f"{_normalize_known_domain('example.com')!r} within a different parent domain"
    )
    assert finding.message == expected_message  # nosec B101


def test_analyze_url_detects_deceptive_subdomain_mid_host() -> None:
    url = "https://login.example.com.evil.net"
    findings = analyze_url(url, known_domains=["example.com"])
    indicators = _indicator_set(findings)
    assert "deceptive-subdomain" in indicators  # nosec B101


def test_analyze_url_detects_deceptive_subdomain_after_noise() -> None:
    url = "https://secureexample.com.example.com.bad.net"
    findings = analyze_url(url, known_domains=["example.com"])
    indicators = _indicator_set(findings)
    assert "deceptive-subdomain" in indicators  # nosec B101


def test_analyze_url_ignores_legitimate_subdomain() -> None:
    url = "https://support.example.com"
    findings = analyze_url(url, known_domains=["", "example.com"])
    indicators = _indicator_set(findings)
    assert "lookalike-domain" not in indicators  # nosec B101


def test_analyze_url_ignores_legitimate_multi_label_suffix_subdomain() -> None:
    url = "https://support.example.co.uk"
    findings = analyze_url(url, known_domains=["example.co.uk"])
    indicators = _indicator_set(findings)
    assert "lookalike-domain" not in indicators  # nosec B101


def test_analyze_text_for_phishing_aggregates_findings() -> None:
    text = """
    Your package could not be delivered. Visit http://delivery-status.link immediately
    or https://secure-login.example.com to verify your address.
    """
    findings = analyze_text_for_phishing(text, known_domains=["delivery-status.com"])
    indicators = _indicator_set(findings)
    assert "insecure-scheme" in indicators  # nosec B101
    assert "suspicious-tld" in indicators  # nosec B101
    assert any(  # nosec B101
        finding.indicator == "lookalike-domain" and "delivery-status" in finding.message
        for finding in findings
    )


def test_analyze_url_handles_missing_hostname() -> None:
    findings = analyze_url("http:///reset-password", known_domains=["example.com"])
    indicators = _indicator_set(findings)
    assert indicators == {"insecure-scheme"}  # nosec B101


def test_analyze_url_handles_single_label_hosts() -> None:
    assert analyze_url("https://localhost") == []  # nosec B101


def test_registrable_domain_for_handles_empty_hostname() -> None:
    assert _registrable_domain_for("") == ""  # nosec B101


def test_registrable_domain_for_fallback_when_suffix_unknown() -> None:
    assert _registrable_domain_for("internal.service.internal") == "service.internal"  # nosec B101


def test_registrable_domain_for_handles_trailing_dot_and_empty_labels() -> None:
    assert _registrable_domain_for("example.com.") == "example.com"  # nosec B101
    assert _registrable_domain_for(".") == ""  # nosec B101


def test_split_registrable_domain_handles_edge_cases() -> None:
    assert _split_registrable_domain("") == ("", "")  # nosec B101
    assert _split_registrable_domain("localhost") == ("localhost", "")  # nosec B101


def test_analyze_url_skips_known_domains_without_registrable_label() -> None:
    findings = analyze_url("https://example.org", known_domains=["."])
    assert "lookalike-domain" not in _indicator_set(findings)  # nosec B101


def test_analyze_url_skips_known_domain_with_trailing_dot() -> None:
    findings = analyze_url("https://support.example.com", known_domains=["example.com."])
    assert "lookalike-domain" not in _indicator_set(findings)  # nosec B101


def test_analyze_url_handles_hostname_with_only_dots() -> None:
    findings = analyze_url("https://./", known_domains=["example.com"])
    assert "lookalike-domain" not in _indicator_set(findings)  # nosec B101


def test_analyze_url_handles_hostname_with_trailing_dot() -> None:
    findings = analyze_url("https://example.com./", known_domains=["example.com"])
    indicators = _indicator_set(findings)
    assert "deceptive-subdomain" not in indicators  # nosec B101
    assert "lookalike-domain" not in indicators  # nosec B101


def test_analyze_url_deceptive_subdomain_requires_label_boundary() -> None:
    findings = analyze_url("https://secureexample.com", known_domains=["example.com"])
    indicators = _indicator_set(findings)
    assert "deceptive-subdomain" not in indicators  # nosec B101


def test_analyze_url_deceptive_subdomain_normalises_known_domain() -> None:
    url = "https://example.com.attacker.org"
    findings = analyze_url(url, known_domains=[" Example.COM. "])
    indicators = _indicator_set(findings)
    assert "deceptive-subdomain" in indicators  # nosec B101
