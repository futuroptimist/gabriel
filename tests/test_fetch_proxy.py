from __future__ import annotations

from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import Mapping

import pytest

from gabriel.security import (
    AllowlistedFetchProxy,
    FetchLogEntry,
    FetchNotAllowed,
    FetchResult,
)


@dataclass(slots=True)
class StubTransport:
    response: FetchResult
    should_raise: Exception | None = None
    requests: list[tuple[str, Mapping[str, str], bytes | None, float | None]] = field(
        init=False, default_factory=list
    )

    def __call__(self, request, timeout):  # noqa: D401 - protocol compatible callable
        if self.should_raise is not None:
            raise self.should_raise
        headers = {key: value for key, value in request.header_items()}
        self.requests.append((request.full_url, headers, request.data, timeout))
        return self.response


def make_response(url: str) -> FetchResult:
    return FetchResult(url=url, status_code=200, headers={"content-type": "text/plain"}, body=b"ok")


def test_fetch_proxy_allows_allowlisted_domain() -> None:
    transport = StubTransport(response=make_response("https://example.com/resource"))
    proxy = AllowlistedFetchProxy(["example.com"], transport=transport)

    result = proxy.fetch(
        "https://example.com/resource",
        headers={"User-Agent": "Gabriel"},
        timeout=1.5,
    )

    assert result.body == b"ok"
    assert transport.requests[0][0] == "https://example.com/resource"
    header_snapshot = {key.lower(): value for key, value in transport.requests[0][1].items()}
    assert header_snapshot["user-agent"] == "Gabriel"
    assert transport.requests[0][2:] == (None, 1.5)
    assert len(proxy.audit_log) == 1
    entry = proxy.audit_log[0]
    assert entry.allowed is True
    assert entry.status_code == 200
    assert entry.reason is None


def test_fetch_proxy_denies_unlisted_domain() -> None:
    proxy = AllowlistedFetchProxy(["example.com"])

    with pytest.raises(FetchNotAllowed) as excinfo:
        proxy.fetch("https://evil.test")

    assert "not allow-listed" in str(excinfo.value)
    assert len(proxy.audit_log) == 1
    entry = proxy.audit_log[0]
    assert entry.allowed is False
    assert entry.status_code is None


def test_fetch_proxy_requires_https() -> None:
    proxy = AllowlistedFetchProxy(["example.com"], require_https=True)

    with pytest.raises(FetchNotAllowed):
        proxy.fetch("http://example.com/insecure")

    assert proxy.audit_log == ()


def test_fetch_proxy_allows_http_when_disabled() -> None:
    transport = StubTransport(response=make_response("http://example.com/check"))
    proxy = AllowlistedFetchProxy(["example.com"], require_https=False, transport=transport)

    proxy.fetch("http://example.com/check")

    assert proxy.audit_log[0].allowed is True


def test_fetch_proxy_wildcard_support() -> None:
    transport = StubTransport(response=make_response("https://api.example.com/data"))
    proxy = AllowlistedFetchProxy(["*.example.com"], transport=transport)

    proxy.fetch("https://sub.api.example.com/data")

    assert proxy.audit_log[0].allowed is True
    assert transport.requests[0][0] == "https://sub.api.example.com/data"


def test_fetch_proxy_leading_dot_support() -> None:
    transport = StubTransport(response=make_response("https://beta.example.net/data"))
    proxy = AllowlistedFetchProxy([".example.net"], transport=transport)

    proxy.fetch("https://api.example.net/data")

    assert proxy.audit_log[0].allowed is True


def test_fetch_proxy_requires_matching_port() -> None:
    transport = StubTransport(response=make_response("https://api.example.com:8443/health"))
    proxy = AllowlistedFetchProxy(["https://api.example.com:8443"], transport=transport)

    proxy.fetch("https://api.example.com:8443/health")

    assert proxy.audit_log[0].allowed is True

    with pytest.raises(FetchNotAllowed):
        proxy.fetch("https://api.example.com:443/health")


def test_fetch_proxy_reports_transport_errors() -> None:
    error = RuntimeError("network down")
    transport = StubTransport(response=make_response("https://example.com"), should_raise=error)
    proxy = AllowlistedFetchProxy(["example.com"], transport=transport)

    with pytest.raises(RuntimeError):
        proxy.fetch("https://example.com")

    assert len(proxy.audit_log) == 1
    entry = proxy.audit_log[0]
    assert isinstance(entry, FetchLogEntry)
    assert entry.allowed is True
    assert entry.reason == "network down"
    assert entry.status_code is None


def test_fetch_proxy_clear_audit_log() -> None:
    transport = StubTransport(response=make_response("https://example.com"))
    proxy = AllowlistedFetchProxy(["example.com"], transport=transport)
    proxy.fetch("https://example.com")
    assert proxy.audit_log
    proxy.clear_audit_log()
    assert proxy.audit_log == ()


def test_fetch_proxy_rejects_empty_allowlist() -> None:
    with pytest.raises(ValueError):
        AllowlistedFetchProxy([])


def test_fetch_proxy_rejects_invalid_scheme() -> None:
    with pytest.raises(ValueError):
        AllowlistedFetchProxy(["ftp://example.com"])


def test_fetch_proxy_rejects_blank_entry() -> None:
    with pytest.raises(ValueError):
        AllowlistedFetchProxy(["   "])


def test_fetch_proxy_rejects_invalid_port_format() -> None:
    with pytest.raises(ValueError):
        AllowlistedFetchProxy(["example.com:"])


def test_fetch_proxy_rejects_invalid_hostname_characters() -> None:
    with pytest.raises(ValueError):
        AllowlistedFetchProxy(["exa mple.com"])


def test_fetch_proxy_rejects_non_http_scheme_at_fetch_time() -> None:
    proxy = AllowlistedFetchProxy(["example.com"])

    with pytest.raises(FetchNotAllowed):
        proxy.fetch("mailto:user@example.com")


def test_fetch_proxy_rejects_missing_hostname() -> None:
    proxy = AllowlistedFetchProxy(["example.com"])

    with pytest.raises(FetchNotAllowed):
        proxy.fetch("https:///missing-host")


def test_fetch_proxy_default_transport(monkeypatch: pytest.MonkeyPatch) -> None:
    captured = SimpleNamespace(request=None, timeout=None)

    class DummyResponse:
        def __init__(self) -> None:
            self.headers = {"content-type": "application/json"}

        def __enter__(self) -> "DummyResponse":
            return self

        def __exit__(self, exc_type, exc, tb) -> bool:
            return False

        def read(self) -> bytes:
            return b"{}"

        def getcode(self) -> int:
            return 204

    def fake_urlopen(request, timeout=None):
        captured.request = request
        captured.timeout = timeout
        return DummyResponse()

    monkeypatch.setattr("gabriel.security.fetch_proxy.urlopen", fake_urlopen)

    proxy = AllowlistedFetchProxy(["example.com"])
    result = proxy.fetch("https://example.com/status", timeout=2.0)

    assert result.status_code == 204
    assert result.body == b"{}"
    assert captured.request.full_url == "https://example.com/status"
    assert captured.timeout == 2.0
    assert proxy.audit_log[0].status_code == 204


def test_effective_port_handles_unknown_scheme() -> None:
    assert AllowlistedFetchProxy._effective_port("ws", None) is None
