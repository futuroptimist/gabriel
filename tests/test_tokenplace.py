from __future__ import annotations

import json
from typing import Any
from urllib import request

import pytest

from gabriel.tokenplace import TokenPlaceClient, TokenPlaceError


class DummyResponse:
    """Simple stand-in for :class:`urllib.response.addinfourl`."""

    def __init__(self, payload: Any, *, status: int = 200) -> None:
        """Serialize ``payload`` to bytes and remember the response status."""

        if isinstance(payload, bytes | bytearray):
            self._body = bytes(payload)
        elif isinstance(payload, str):
            self._body = payload.encode("utf-8")
        else:
            self._body = json.dumps(payload).encode("utf-8")
        self.status = status

    def read(self) -> bytes:
        return self._body

    def getcode(self) -> int:
        return self.status

    def __enter__(self) -> DummyResponse:
        """Return ``self`` so the object can be used as a context manager."""
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        """Accept context manager arguments without suppressing exceptions."""
        return None


def _capture_request(monkeypatch: pytest.MonkeyPatch, response: DummyResponse):
    captured: dict[str, Any] = {}

    def fake_urlopen(req: request.Request, *, timeout: float):
        captured["url"] = req.full_url
        captured["data"] = req.data
        captured["headers"] = {k.title(): v for k, v in req.header_items()}
        captured["timeout"] = timeout
        return response

    monkeypatch.setattr(request, "urlopen", fake_urlopen)
    return captured


def test_infer_sends_expected_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    response = DummyResponse(
        {
            "text": "Encrypted success.",
            "model": "llama3",
            "usage": {"prompt_tokens": 12, "completion_tokens": 20},
        }
    )
    captured = _capture_request(monkeypatch, response)

    client = TokenPlaceClient("https://relay.local/api", api_key="secret", timeout=5)
    completion = client.infer(
        "Secure prompt",
        model="llama3",
        temperature=0.1,
        metadata={"request_id": "abc-123"},
    )

    assert completion.text == "Encrypted success."  # nosec B101
    assert completion.model == "llama3"  # nosec B101
    assert completion.usage == {"prompt_tokens": 12, "completion_tokens": 20}  # nosec B101

    assert captured["url"] == "https://relay.local/api/v1/infer"  # nosec B101
    assert captured["timeout"] == 5  # nosec B101
    headers = captured["headers"]
    assert headers["Content-Type"] == "application/json"  # nosec B101
    assert headers["Authorization"] == "Bearer secret"  # nosec B101

    payload = json.loads(captured["data"].decode("utf-8"))
    assert payload == {
        "prompt": "Secure prompt",
        "model": "llama3",
        "temperature": 0.1,
        "metadata": {"request_id": "abc-123"},
    }  # nosec B101


def test_infer_requires_text_field(monkeypatch: pytest.MonkeyPatch) -> None:
    response = DummyResponse({"model": "llama3"})
    _capture_request(monkeypatch, response)

    client = TokenPlaceClient("https://relay.local")
    with pytest.raises(TokenPlaceError):
        client.infer("Hello")


def test_infer_uses_model_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    response = DummyResponse({"text": "ok", "usage": None})
    captured = _capture_request(monkeypatch, response)

    client = TokenPlaceClient("https://relay.local")
    completion = client.infer("prompt", model="llama3")
    assert completion.model == "llama3"  # nosec B101
    assert completion.usage == {}  # nosec B101
    assert json.loads(captured["data"].decode("utf-8"))["model"] == "llama3"  # nosec B101


def test_infer_rejects_non_dict_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    response = DummyResponse(["unexpected"])
    _capture_request(monkeypatch, response)

    client = TokenPlaceClient("https://relay.local")
    with pytest.raises(TokenPlaceError):
        client.infer("prompt")


def test_health_check_parses_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    response = DummyResponse({"status": "OK"})
    captured = _capture_request(monkeypatch, response)

    client = TokenPlaceClient("https://relay.local")
    assert client.check_health() is True  # nosec B101
    assert captured["url"] == "https://relay.local/v1/health"  # nosec B101


def test_health_check_handles_empty_body(monkeypatch: pytest.MonkeyPatch) -> None:
    response = DummyResponse(b"")
    _capture_request(monkeypatch, response)

    client = TokenPlaceClient("https://relay.local")
    assert client.check_health() is False  # nosec B101


def test_health_check_returns_false_for_non_dict(monkeypatch: pytest.MonkeyPatch) -> None:
    response = DummyResponse(["not-a-dict"])
    _capture_request(monkeypatch, response)

    client = TokenPlaceClient("https://relay.local")
    assert client.check_health() is False  # nosec B101


def test_base_url_validation() -> None:
    with pytest.raises(ValueError):
        TokenPlaceClient("relay.local")


def test_request_raises_on_error_status(monkeypatch: pytest.MonkeyPatch) -> None:
    response = DummyResponse("fail", status=502)
    _capture_request(monkeypatch, response)

    client = TokenPlaceClient("https://relay.local")
    with pytest.raises(TokenPlaceError):
        client.infer("prompt")


def test_request_rejects_invalid_json(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_urlopen(req: request.Request, *, timeout: float):
        return DummyResponse("not json", status=200)

    monkeypatch.setattr(request, "urlopen", fake_urlopen)

    client = TokenPlaceClient("https://relay.local")
    with pytest.raises(TokenPlaceError):
        client.check_health()
