"""Helpers for interacting with a local token.place relay."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urljoin, urlparse


class TokenPlaceError(RuntimeError):
    """Raised when token.place returns an error or unexpected payload."""


@dataclass(frozen=True, slots=True)
class TokenPlaceCompletion:
    """Represents a successful completion returned by token.place."""

    text: str
    model: str
    usage: dict[str, Any]
    raw: dict[str, Any]


@dataclass(slots=True)
class TokenPlaceClient:
    """Small HTTP client for the token.place relay API."""

    base_url: str
    api_key: str | None = None
    timeout: float = 10.0
    _base_url: str = field(init=False, repr=False)

    def __post_init__(self) -> None:
        parsed = urlparse(self.base_url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("base_url must include scheme and host, e.g. https://relay.local")
        normalized = self.base_url.rstrip("/") + "/"
        object.__setattr__(self, "_base_url", normalized)

    def infer(
        self,
        prompt: str,
        *,
        model: str | None = None,
        temperature: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> TokenPlaceCompletion:
        """Send ``prompt`` to token.place and return the resulting completion."""

        payload: dict[str, Any] = {"prompt": prompt}
        if model is not None:
            payload["model"] = model
        if temperature is not None:
            payload["temperature"] = temperature
        if metadata:
            payload["metadata"] = metadata

        response = self._request("POST", "v1/infer", payload)
        if not isinstance(response, dict):
            raise TokenPlaceError("token.place returned an unexpected payload")

        text = response.get("text") or response.get("response")
        if not isinstance(text, str) or not text:
            raise TokenPlaceError("token.place response did not include generated text")

        model_name = response.get("model")
        if not isinstance(model_name, str) or not model_name:
            model_name = model or "unknown"

        usage_raw = response.get("usage")
        usage: dict[str, Any]
        if isinstance(usage_raw, dict):
            usage = dict(usage_raw)
        else:
            usage = {}

        return TokenPlaceCompletion(text=text, model=model_name, usage=usage, raw=response)

    def check_health(self) -> bool:
        """Return ``True`` if the relay reports an OK status."""

        response = self._request("GET", "v1/health")
        if not isinstance(response, dict):
            return False
        status = response.get("status")
        return isinstance(status, str) and status.lower() == "ok"

    def _request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
        url = urljoin(self._base_url, path)
        data: bytes | None = None
        headers = {"Accept": "application/json"}
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        request = urllib.request.Request(url, data=data, method=method, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:  # nosec B310
                status = getattr(response, "status", response.getcode())
                body = response.read()
        except urllib.error.HTTPError as exc:  # pragma: no cover - error path exercised via URLError
            detail = exc.read().decode("utf-8", "replace").strip()
            message = f"token.place responded with HTTP {exc.code}: {detail}"
            raise TokenPlaceError(message) from exc
        except urllib.error.URLError as exc:  # pragma: no cover - network failure path
            message = f"Failed to reach token.place at {url}: {exc.reason}"
            raise TokenPlaceError(message) from exc

        if status >= 400:
            body_preview = body.decode("utf-8", "replace").strip()
            raise TokenPlaceError(
                f"token.place responded with HTTP {status}: {body_preview}"
            )

        if not body:
            return {}

        try:
            return json.loads(body.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise TokenPlaceError("token.place returned invalid JSON") from exc


__all__ = [
    "TokenPlaceClient",
    "TokenPlaceCompletion",
    "TokenPlaceError",
]
