"""Tests for credential audit log helpers."""

from __future__ import annotations

import io
import json
import types
from datetime import datetime, timedelta, timezone

import pytest

from gabriel.security import (
    FindingSeverity,
    TokenAuditRecord,
    analyze_expired_tokens,
    load_token_audit_records,
)
from gabriel.security import audit as audit_module


def _dt(text: str) -> datetime:
    """Parse ISO timestamps with a UTC fallback."""

    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    return datetime.fromisoformat(text).astimezone(timezone.utc)


def test_load_token_audit_records_supports_json_array() -> None:
    payload = json.dumps(
        [
            {
                "token_id": "alpha",
                "issued_at": "2024-08-01T00:00:00Z",
                "expires_at": "2024-08-08T00:00:00Z",
                "status": "active",
                "scopes": ["contents:read"],
            }
        ]
    )
    records = load_token_audit_records(io.StringIO(payload))
    assert len(records) == 1
    record = records[0]
    assert record.token_id == "alpha"
    assert record.expires_at == _dt("2024-08-08T00:00:00Z")
    assert record.scopes == ("contents:read",)


def test_load_token_audit_records_supports_json_lines(tmp_path) -> None:
    path = tmp_path / "audit.log"
    path.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "token_id": "bravo",
                        "issued_at": "2024-08-01T00:00:00+00:00",
                        "expires_at": "2024-08-05T00:00:00+00:00",
                        "status": "active",
                        "scopes": "repo,workflow",
                    }
                ),
                json.dumps(
                    {
                        "token_id": "charlie",
                        "issued_at": "2024-08-02T00:00:00+00:00",
                        "expires_at": "2024-08-03T00:00:00+00:00",
                        "status": "revoked",
                    }
                ),
            ]
        ),
        encoding="utf-8",
    )
    records = load_token_audit_records(path)
    assert [record.token_id for record in records] == ["bravo", "charlie"]
    assert records[0].scopes == ("repo", "workflow")
    assert records[1].status == "revoked"


def test_analyze_expired_tokens_flags_usage_after_expiry() -> None:
    now = datetime(2024, 8, 10, 12, tzinfo=timezone.utc)
    records = [
        TokenAuditRecord(
            token_id="delta",
            issued_at=now - timedelta(days=9),
            expires_at=now - timedelta(days=1, hours=2),
            last_seen_at=now - timedelta(hours=1),
            scopes=("contents:read",),
            status="active",
        ),
        TokenAuditRecord(
            token_id="echo",
            issued_at=now - timedelta(days=20),
            expires_at=now - timedelta(days=2),
            last_seen_at=None,
            scopes=("repo",),
            status="active",
        ),
        TokenAuditRecord(
            token_id="golf",
            issued_at=now - timedelta(days=15),
            expires_at=now - timedelta(days=5),
            status="revoked",
        ),
        TokenAuditRecord(
            token_id="foxtrot",
            issued_at=now - timedelta(days=5),
            expires_at=now - timedelta(days=1),
            revoked_at=now - timedelta(hours=2),
            status="revoked",
        ),
    ]
    findings = analyze_expired_tokens(records, now=now)
    assert len(findings) == 3
    high = next(f for f in findings if f.token_id == "delta")
    medium = next(f for f in findings if f.token_id == "echo")
    revoked = next(f for f in findings if f.token_id == "golf")
    assert high.severity is FindingSeverity.HIGH
    assert "used" in high.summary.lower()
    assert "delta" in high.details
    assert medium.severity is FindingSeverity.MEDIUM
    assert "expired" in medium.summary.lower()
    assert revoked.severity is FindingSeverity.MEDIUM
    assert "Reported status" not in revoked.details


def test_analyze_expired_tokens_respects_grace_period() -> None:
    now = datetime(2024, 8, 10, 12, tzinfo=timezone.utc)
    record = TokenAuditRecord(
        token_id="golf",
        issued_at=now - timedelta(days=3),
        expires_at=now - timedelta(minutes=2),
        status="active",
    )
    assert analyze_expired_tokens([record], now=now, grace_period=timedelta(minutes=5)) == []
    findings = analyze_expired_tokens([record], now=now, grace_period=timedelta(seconds=30))
    assert len(findings) == 1
    assert findings[0].severity is FindingSeverity.MEDIUM


def test_token_audit_record_helpers_cover_edge_cases() -> None:
    now = datetime(2024, 8, 10, tzinfo=timezone.utc)
    payload = {
        "token_id": "hotel",
        "issued_at": datetime(2024, 8, 1, 12, 0, 0),  # naive datetime exercises tz normalization
        "expires_at": datetime(2024, 8, 5, 12, 0, 0),
        "scopes": None,
    }
    record = TokenAuditRecord.from_dict(payload)
    assert record.issued_at.tzinfo is not None
    assert record.expired(now=now)
    delta = record.expired_for(now=now)
    assert isinstance(delta, timedelta)
    assert delta.days >= 4


def test_load_token_audit_records_handles_empty_and_invalid_payloads(tmp_path) -> None:
    blank = tmp_path / "blank.log"
    blank.write_text("  \n  ", encoding="utf-8")
    assert load_token_audit_records(blank) == []

    invalid = io.StringIO(json.dumps({"token": "missing"}))
    with pytest.raises(ValueError):
        load_token_audit_records(invalid)


def test_load_token_audit_records_rejects_non_list_json(monkeypatch) -> None:
    def fake_loads(_: str) -> object:
        return {"oops": True}

    monkeypatch.setattr(audit_module, "json", types.SimpleNamespace(loads=fake_loads))
    with pytest.raises(ValueError):
        load_token_audit_records(io.StringIO("[{}]"))


def test_token_audit_record_from_dict_requires_timestamps() -> None:
    with pytest.raises(ValueError):
        TokenAuditRecord.from_dict({"token_id": "invalid", "issued_at": "2024-08-01T00:00:00Z"})
    with pytest.raises(ValueError):
        TokenAuditRecord.from_dict(
            {
                "token_id": "invalid",
                "issued_at": "2024-08-01T00:00:00Z",
                "expires_at": None,
            }
        )
