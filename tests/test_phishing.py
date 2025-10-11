# bandit:skip-file

from __future__ import annotations

import pytest

from gabriel.phishing import (
    PhishingFinding,
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


def test_analyze_url_flags_known_shorteners() -> None:
    url = "https://bit.ly/reset-password"
    findings = analyze_url(url)
    indicators = _indicator_set(findings)
    assert "url-shortener" in indicators  # nosec B101
    [finding] = [f for f in findings if f.indicator == "url-shortener"]
    assert finding.severity == "medium"  # nosec B101


def test_analyze_url_flags_nonstandard_port_usage() -> None:
    url = "https://example.com:8443/login"
    findings = analyze_url(url)
    indicators = _indicator_set(findings)
    assert "nonstandard-port" in indicators  # nosec B101
    [finding] = [f for f in findings if f.indicator == "nonstandard-port"]
    assert finding.severity == "medium"  # nosec B101


def test_analyze_url_handles_invalid_port() -> None:
    url = "https://example.com:abc/login"
    findings = analyze_url(url)
    indicators = _indicator_set(findings)
    assert indicators == {"invalid-port"}  # nosec B101
    [finding] = findings
    assert finding.severity == "medium"  # nosec B101


def test_analyze_url_detects_external_redirect_parameters() -> None:
    url = "https://example.com/login?redirect=https://malicious.co/verify"
    findings = analyze_url(url)
    indicators = _indicator_set(findings)
    assert "external-redirect" in indicators  # nosec B101
    [finding] = [f for f in findings if f.indicator == "external-redirect"]
    assert "malicious.co" in finding.message  # nosec B101


def test_analyze_url_ignores_internal_redirect_parameters() -> None:
    url = "https://example.com/login?redirect=https://example.com/dashboard"
    findings = analyze_url(url)
    indicators = _indicator_set(findings)
    assert "external-redirect" not in indicators  # nosec B101


def test_analyze_url_ignores_redirect_edge_cases() -> None:
    url = (
        "https://example.com/login?redirect=&"
        "go=/internal"
        "&jump=https://"
        "&next=https://example.com:443/welcome"
        "&again=https://malicious.co"
        "&again=https://malicious.co/profile"
    )
    findings = analyze_url(url)
    indicators = _indicator_set(findings)
    assert indicators == {"external-redirect"}  # nosec B101
    matching = [f for f in findings if f.indicator == "external-redirect"]
    assert len(matching) == 1  # nosec B101
    assert matching[0].message.endswith("malicious.co")  # nosec B101


def test_analyze_url_flags_executable_download_targets() -> None:
    url = "https://example.com/files/Invoice.pdf.exe"
    findings = analyze_url(url)
    indicators = _indicator_set(findings)
    assert "suspicious-download" in indicators  # nosec B101
    [finding] = [f for f in findings if f.indicator == "suspicious-download"]
    assert finding.severity == "high"  # nosec B101
    assert "Invoice.pdf.exe" in finding.message  # nosec B101


def test_analyze_url_flags_archive_downloads_in_query_parameters() -> None:
    url = "https://example.com/download?file=backup%20(1).zip"
    findings = analyze_url(url)
    indicators = _indicator_set(findings)
    assert "suspicious-download" in indicators  # nosec B101
    matching = [f for f in findings if f.indicator == "suspicious-download"]
    assert matching[0].severity == "medium"  # nosec B101
    assert "backup (1).zip" in matching[0].message  # nosec B101


def test_analyze_url_ignores_extension_only_tokens() -> None:
    url = "https://example.com/download?file=.exe"
    findings = analyze_url(url)
    indicators = _indicator_set(findings)
    assert "suspicious-download" not in indicators  # nosec B101


def test_analyze_url_deduplicates_repeated_download_targets() -> None:
    url = (
        "https://example.com/download?primary=invoice.exe"
        "&secondary=invoice.exe"
        "&fallback=invoice.EXE"
    )
    findings = analyze_url(url)
    matches = [f for f in findings if f.indicator == "suspicious-download"]
    assert len(matches) == 1  # nosec B101
    assert matches[0].severity == "high"  # nosec B101


def test_analyze_url_flags_fragment_download_reference() -> None:
    url = "https://example.com/#payload.7z"
    findings = analyze_url(url)
    matching = [f for f in findings if f.indicator == "suspicious-download"]
    assert len(matching) == 1  # nosec B101
    assert matching[0].severity == "medium"  # nosec B101
    assert "via fragment" in matching[0].message  # nosec B101


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
