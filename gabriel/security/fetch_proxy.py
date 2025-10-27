"""Allow-listed HTTP fetch proxy with domain verification and auditing."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import logging
from typing import Callable, Iterable, Mapping, MutableSequence, Sequence
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen
import time

__all__ = [
    "AllowlistedFetchProxy",
    "FetchLogEntry",
    "FetchNotAllowed",
    "FetchResult",
]


_LOGGER = logging.getLogger(__name__)


@dataclass(slots=True, frozen=True)
class FetchResult:
    """Result returned by :class:`AllowlistedFetchProxy` fetch operations."""

    url: str
    status_code: int
    headers: Mapping[str, str]
    body: bytes


@dataclass(slots=True, frozen=True)
class FetchLogEntry:
    """Audit log entry describing a proxy fetch attempt."""

    timestamp: datetime
    url: str
    method: str
    allowed: bool
    status_code: int | None
    duration: float | None
    reason: str | None = None


class FetchNotAllowed(RuntimeError):
    """Raised when a URL violates the fetch proxy security policy."""


@dataclass(slots=True, frozen=True)
class _DomainRule:
    host: str
    match_subdomains: bool
    port: int | None

    def matches(self, host: str, port: int | None) -> bool:
        """Return ``True`` when ``host`` and ``port`` match this rule."""
        host = host.lower()
        if self.port is not None and self.port != (port or self.port):
            return False
        if host == self.host:
            return True
        return self.match_subdomains and host.endswith(f".{self.host}")


Transport = Callable[[Request, float | None], FetchResult]


def _default_transport(request: Request, timeout: float | None = None) -> FetchResult:
    with urlopen(request, timeout=timeout) as response:  # nosec: B310 - domain is verified ahead of time
        body = response.read()
        status = response.getcode() or 0
        headers = {key: value for key, value in response.headers.items()}
    return FetchResult(url=request.full_url, status_code=status, headers=headers, body=body)


class AllowlistedFetchProxy:
    """Proxy that guards outbound HTTP(S) requests behind a domain allow-list."""

    def __init__(
        self,
        allowed_domains: Iterable[str],
        *,
        require_https: bool = True,
        transport: Transport | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self._rules: Sequence[_DomainRule] = tuple(self._parse_rule(rule) for rule in allowed_domains)
        if not self._rules:
            raise ValueError("allowed_domains must contain at least one hostname")
        self.require_https = require_https
        self._transport = transport or _default_transport
        self._logger = logger or _LOGGER
        self._audit_log: MutableSequence[FetchLogEntry] = []

    @property
    def audit_log(self) -> Sequence[FetchLogEntry]:
        """Return immutable view of recorded fetch attempts."""
        return tuple(self._audit_log)

    def clear_audit_log(self) -> None:
        """Remove all recorded audit entries."""
        self._audit_log.clear()

    def fetch(
        self,
        url: str,
        *,
        method: str = "GET",
        headers: Mapping[str, str] | None = None,
        data: bytes | None = None,
        timeout: float | None = None,
    ) -> FetchResult:
        """Fetch a URL after enforcing protocol and domain policies."""

        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            raise FetchNotAllowed("Only http:// or https:// URLs are permitted")
        if self.require_https and parsed.scheme != "https":
            raise FetchNotAllowed("HTTPS is required for outbound requests")
        host = parsed.hostname
        if host is None:
            raise FetchNotAllowed("URL is missing a hostname")
        port = self._effective_port(parsed.scheme, parsed.port)
        if not self._is_allowed(host, port):
            host_display = f"{host}:{port}" if port is not None else host
            reason = f"Host {host_display} is not allow-listed"
            entry = FetchLogEntry(
                timestamp=datetime.now(tz=timezone.utc),
                url=url,
                method=method.upper(),
                allowed=False,
                status_code=None,
                duration=None,
                reason=reason,
            )
            self._audit_log.append(entry)
            self._logger.warning("Denied outbound request to %s: %s", url, entry.reason)
            raise FetchNotAllowed(entry.reason)

        request = Request(url, data=data, method=method.upper())
        if headers:
            for key, value in headers.items():
                request.add_header(key, value)

        start = time.perf_counter()
        try:
            result = self._transport(request, timeout)
        except URLError as exc:  # pragma: no cover - urllib specific branch, hits in integration tests
            duration = time.perf_counter() - start
            entry = FetchLogEntry(
                timestamp=datetime.now(tz=timezone.utc),
                url=url,
                method=method.upper(),
                allowed=True,
                status_code=None,
                duration=duration,
                reason=str(exc.reason or exc),
            )
            self._audit_log.append(entry)
            self._logger.error("Fetch to %s failed: %s", url, entry.reason)
            raise
        except Exception as exc:
            duration = time.perf_counter() - start
            entry = FetchLogEntry(
                timestamp=datetime.now(tz=timezone.utc),
                url=url,
                method=method.upper(),
                allowed=True,
                status_code=None,
                duration=duration,
                reason=str(exc),
            )
            self._audit_log.append(entry)
            self._logger.error("Fetch to %s failed: %s", url, entry.reason)
            raise
        else:
            duration = time.perf_counter() - start
            entry = FetchLogEntry(
                timestamp=datetime.now(tz=timezone.utc),
                url=result.url,
                method=method.upper(),
                allowed=True,
                status_code=result.status_code,
                duration=duration,
                reason=None,
            )
            self._audit_log.append(entry)
            self._logger.info(
                "Fetched %s %s status=%s duration=%.3fs",
                method.upper(),
                result.url,
                result.status_code,
                duration,
            )
            return result

    def _is_allowed(self, host: str, port: int | None) -> bool:
        normalized_host = host.lower().rstrip(".")
        for rule in self._rules:
            if rule.matches(normalized_host, port):
                return True
        return False

    def _parse_rule(self, rule: str) -> _DomainRule:
        text = rule.strip()
        if not text:
            raise ValueError("Allow-list entries must be non-empty")
        match_subdomains = False
        port: int | None = None
        host_text = text
        if "://" in host_text:
            parsed = urlparse(host_text)
            if parsed.scheme and parsed.scheme not in {"http", "https"}:
                raise ValueError(f"Unsupported scheme in allow-list entry: {text}")
            host_text = parsed.netloc
            port = parsed.port
        if host_text.startswith("*."):
            match_subdomains = True
            host_text = host_text[2:]
        elif host_text.startswith("."):
            match_subdomains = True
            host_text = host_text.lstrip(".")
        if ":" in host_text:
            host_part, port_part = host_text.rsplit(":", 1)
            host_text = host_part
            if not port_part:
                raise ValueError(f"Invalid port in allow-list entry: {text}")
            try:
                port = int(port_part)
            except ValueError as exc:  # pragma: no cover - validation guard
                raise ValueError(f"Invalid port in allow-list entry: {text}") from exc
        host_text = host_text.strip().lower().rstrip(".")
        if not host_text or any(ch in host_text for ch in " /?#"):
            raise ValueError(f"Invalid hostname in allow-list entry: {text}")
        return _DomainRule(host=host_text, match_subdomains=match_subdomains, port=port)

    @staticmethod
    def _effective_port(scheme: str, port: int | None) -> int | None:
        if port is not None:
            return port
        if scheme == "http":
            return 80
        if scheme == "https":
            return 443
        return None
