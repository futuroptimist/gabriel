"""Egress control policy enforcement for Gabriel agents."""

from __future__ import annotations

import ipaddress
import json
import logging
import os
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class EgressPolicyViolation(RuntimeError):
    """Raised when an outbound request violates the configured egress policy."""


def _env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _default_allowlist_path() -> Path:
    return Path(__file__).with_name("allowlist.json")


@dataclass(slots=True)
class EgressControlPolicy:
    """Enforces outbound network restrictions using a static allowlist."""

    allowlist_path: Path = field(default_factory=_default_allowlist_path)
    safe_mode: bool = field(default_factory=lambda: _env_flag("SAFE_MODE", True))
    allowed_domains: set[str] = field(init=False, default_factory=set)
    allowed_ips: set[str] = field(init=False, default_factory=set)

    def __post_init__(self) -> None:
        """Populate allowlist caches immediately after initialisation."""
        self.reload()

    @classmethod
    def from_env(cls) -> EgressControlPolicy:
        """Return a policy initialised from environment configuration."""

        allowlist_env = os.getenv("EGRESS_ALLOWLIST_PATH")
        path = Path(allowlist_env) if allowlist_env else _default_allowlist_path()
        safe_mode = _env_flag("SAFE_MODE", True)
        return cls(allowlist_path=path, safe_mode=safe_mode)

    def reload(self) -> None:
        """Reload the allowlist from disk."""

        data = self._load_allowlist(self.allowlist_path)
        self.allowed_domains = {
            entry.strip().lower()
            for entry in data.get("domains", [])
            if isinstance(entry, str) and entry.strip()
        }
        self.allowed_ips = {
            entry.strip()
            for entry in data.get("ips", [])
            if isinstance(entry, str) and entry.strip()
        }

    def _load_allowlist(self, path: Path) -> dict[str, Iterable[str]]:
        try:
            with path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except FileNotFoundError as exc:
            message = f"Allowlist file not found: {path}"
            raise RuntimeError(message) from exc
        if not isinstance(payload, dict):
            raise RuntimeError("Allowlist must be a JSON object")

        domains = payload.get("domains", [])
        ips = payload.get("ips", [])
        if not self._validate_entries(domains) or not self._validate_entries(ips):
            raise RuntimeError("Allowlist entries must be strings")

        return {"domains": domains, "ips": ips}

    @staticmethod
    def _validate_entries(entries: Iterable[str]) -> bool:
        return all(isinstance(entry, str) for entry in entries)

    def validate_request(self, target_url: str) -> None:
        """Validate the target URL against the allowlist or raise a violation."""

        parsed = urlparse(target_url)
        host = parsed.hostname
        if not host:
            raise EgressPolicyViolation("Cannot determine host for outbound request")
        if parsed.scheme not in {"http", "https"}:
            raise EgressPolicyViolation("Only HTTP/S egress is permitted")

        if not self.safe_mode:
            logger.debug(
                "SAFE_MODE disabled; skipping allowlist validation",
                extra={"policy": "EgressControl", "reason": "safe_mode_disabled"},
            )
            return

        if not self.allowed_domains and not self.allowed_ips:
            self._log_block(target_url, reason="No allowlist entries configured")
            raise EgressPolicyViolation("SAFE_MODE prevents outbound requests without an allowlist")

        if not self._is_host_allowed(host):
            self._log_block(target_url, reason=f"Host '{host}' not in allowlist")
            raise EgressPolicyViolation(f"Host '{host}' is not allowlisted")

    def _is_host_allowed(self, host: str) -> bool:
        lowered = host.lower()
        if lowered in self.allowed_domains:
            return True
        if any(lowered.endswith(f".{domain}") for domain in self.allowed_domains):
            return True

        if lowered in self.allowed_ips:
            return True
        try:
            ipaddress.ip_address(lowered)
        except ValueError:
            return False
        return lowered in self.allowed_ips

    def _log_block(self, url: str, *, reason: str) -> None:
        logger.warning(
            "Egress blocked: %s", url, extra={"policy": "EgressControl", "reason": reason}
        )


__all__ = ["EgressControlPolicy", "EgressPolicyViolation"]
