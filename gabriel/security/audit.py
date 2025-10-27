"""Audit helpers for token lifecycle reviews.

This module helps security reviewers analyze credential audit logs for
expired tokens that remain active. The helpers prioritize readability and
provide structured findings that downstream tooling or CLIs can surface.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, TextIO


class FindingSeverity(str, Enum):
    """Severity levels for audit findings."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


def _parse_timestamp(value: str | datetime | None) -> datetime | None:
    """Return a timezone-aware ``datetime`` for ``value``.

    The helper accepts ISO-8601 strings (including ``Z`` suffixes) or existing
    ``datetime`` objects. ``None`` values are propagated to the caller.
    """

    if value is None:
        return None
    if isinstance(value, datetime):
        dt = value
    else:
        text = value.strip()
        if text.endswith("Z"):
            text = f"{text[:-1]}+00:00"
        dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


@dataclass(slots=True)
class TokenAuditRecord:
    """Representation of a token lifecycle event in the audit log."""

    token_id: str
    issued_at: datetime
    expires_at: datetime
    last_seen_at: datetime | None = None
    revoked_at: datetime | None = None
    scopes: tuple[str, ...] = ()
    status: str = "active"

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> TokenAuditRecord:
        """Create a record from a JSON payload."""

        try:
            raw_token_id = payload["token_id"]
            raw_issued_at = payload["issued_at"]
            raw_expires_at = payload["expires_at"]
        except KeyError as exc:
            raise ValueError(f"Missing required field: {exc.args[0]}") from exc

        token_id = str(raw_token_id)
        issued_at = _parse_timestamp(raw_issued_at)
        expires_at = _parse_timestamp(raw_expires_at)
        last_seen_at = _parse_timestamp(payload.get("last_seen_at"))
        revoked_at = _parse_timestamp(payload.get("revoked_at"))
        scopes_field = payload.get("scopes", ())
        if isinstance(scopes_field, str):
            scopes: tuple[str, ...] = tuple(
                scope.strip() for scope in scopes_field.split(",") if scope.strip()
            )
        elif isinstance(scopes_field, Sequence):
            scopes = tuple(str(scope) for scope in scopes_field)
        else:
            scopes = ()
        status = str(payload.get("status", "active")).lower()
        if issued_at is None or expires_at is None:
            raise ValueError("issued_at and expires_at must be present in token audit payloads")
        return cls(
            token_id=token_id,
            issued_at=issued_at,
            expires_at=expires_at,
            last_seen_at=last_seen_at,
            revoked_at=revoked_at,
            scopes=scopes,
            status=status,
        )

    def expired(self, *, now: datetime | None = None) -> bool:
        """Return ``True`` when the token should be considered expired."""

        reference = now or datetime.now(timezone.utc)
        return self.expires_at <= reference

    def expired_for(self, *, now: datetime | None = None) -> timedelta:
        """Return how long the token has been expired."""

        reference = now or datetime.now(timezone.utc)
        return reference - self.expires_at


@dataclass(slots=True)
class TokenAuditFinding:
    """Finding describing a risky token lifecycle event."""

    token_id: str
    severity: FindingSeverity
    summary: str
    details: str
    record: TokenAuditRecord


def load_token_audit_records(source: str | Path | TextIO) -> list[TokenAuditRecord]:
    """Parse token audit records from ``source``.

    The audit log may be a JSON array or newline-delimited JSON objects.
    """

    if hasattr(source, "read"):
        text = source.read()
    else:
        text = Path(source).read_text(encoding="utf-8")
    text = text.strip()
    if not text:
        return []
    objects: Iterable[Mapping[str, Any]]
    if text.startswith("["):
        loaded = json.loads(text)
        if not isinstance(loaded, list):
            raise ValueError("Expected a JSON array for audit log contents")
        objects = loaded
    else:
        objects = [json.loads(line) for line in text.splitlines() if line.strip()]
    return [TokenAuditRecord.from_dict(obj) for obj in objects]


def analyze_expired_tokens(
    records: Iterable[TokenAuditRecord],
    *,
    now: datetime | None = None,
    grace_period: timedelta = timedelta(),
) -> list[TokenAuditFinding]:
    """Return findings for tokens that remain active after expiration.

    ``grace_period`` can be used to provide a buffer between the recorded
    expiration time and when a finding should be emitted. This helps avoid
    noisy results when revocation automation may lag by a few minutes.
    """

    reference = now or datetime.now(timezone.utc)
    findings: list[TokenAuditFinding] = []
    for record in records:
        expired_cutoff = record.expires_at + grace_period
        if expired_cutoff > reference:
            continue
        if record.revoked_at and record.revoked_at <= reference:
            continue
        summary: str
        details: str
        if record.last_seen_at and record.last_seen_at > record.expires_at:
            severity = FindingSeverity.HIGH
            summary = "Token used after expiration"
            details = (
                f"Token {record.token_id} was used at "
                f"{record.last_seen_at.isoformat()} even though it expired at "
                f"{record.expires_at.isoformat()}."
            )
        else:
            severity = FindingSeverity.MEDIUM
            summary = "Token expired without revocation"
            details = (
                f"Token {record.token_id} expired at "
                f"{record.expires_at.isoformat()} but has not been revoked as of "
                f"{reference.isoformat()}."
            )
        if record.scopes:
            details += f" Scopes: {', '.join(record.scopes)}."
        if record.status not in {"revoked", "expired"}:
            details += f" Reported status: {record.status}."
        findings.append(
            TokenAuditFinding(
                token_id=record.token_id,
                severity=severity,
                summary=summary,
                details=details,
                record=record,
            )
        )
    return findings


__all__ = [
    "FindingSeverity",
    "TokenAuditRecord",
    "TokenAuditFinding",
    "load_token_audit_records",
    "analyze_expired_tokens",
]
