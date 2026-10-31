from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Literal, cast

import pytest

from gabriel.inference import (
    InferenceError,
    InferenceResult,
    _load_llama_model,
    generate_local_completion,
    generate_relay_completion,
    parse_metadata,
    reset_local_model_cache,
    run_inference,
)


def test_generate_local_completion_uses_stubbed_llama(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    model_path = tmp_path / "model.gguf"
    model_path.write_bytes(b"test")

    def fake_loader(path: str, *, n_ctx: int, n_threads: int | None) -> object:
        class StubLlama:
            def __call__(
                self, prompt: str, *, max_tokens: int, temperature: float, top_p: float
            ) -> dict[str, object]:
                assert path == str(model_path)
                assert prompt == "Run a diagnostic"
                assert max_tokens == 128
                assert temperature == 0.4
                assert top_p == 0.9
                assert n_ctx == 1024
                assert n_threads == 2
                return {"choices": [{"text": " Diagnostic complete."}]}

        return StubLlama()

    monkeypatch.setenv("GABRIEL_MODEL_PATH", str(model_path))
    monkeypatch.setattr("gabriel.inference._load_llama_model", fake_loader)

    result = generate_local_completion(
        "Run a diagnostic",
        max_tokens=128,
        temperature=0.4,
        top_p=0.9,
        n_ctx=1024,
        n_threads=2,
    )

    assert isinstance(result, InferenceResult)
    assert result.mode == "local"
    assert result.text == "Diagnostic complete."
    assert result.metadata["model_path"].endswith("model.gguf")
    assert result.metadata["n_ctx"] == 1024
    assert result.metadata["n_threads"] == 2


def test_generate_local_completion_requires_model_path(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GABRIEL_MODEL_PATH", raising=False)
    with pytest.raises(InferenceError) as excinfo:
        generate_local_completion("hello")
    assert "GABRIEL_MODEL_PATH" in str(excinfo.value)


def test_generate_local_completion_requires_llama_dependency(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    model_path = tmp_path / "model.gguf"
    model_path.write_bytes(b"data")
    monkeypatch.setenv("GABRIEL_MODEL_PATH", str(model_path))
    reset_local_model_cache()
    with pytest.raises(InferenceError) as excinfo:
        generate_local_completion("Check offline mode")
    assert "llama-cpp-python" in str(excinfo.value)


def test_generate_local_completion_rejects_missing_path(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    missing = tmp_path / "missing.gguf"
    monkeypatch.delenv("GABRIEL_MODEL_PATH", raising=False)
    with pytest.raises(InferenceError) as excinfo:
        generate_local_completion("prompt", model_path=missing)
    assert "does not exist" in str(excinfo.value)


def test_generate_local_completion_rejects_directory(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    model_dir = tmp_path / "models"
    model_dir.mkdir()
    with pytest.raises(InferenceError) as excinfo:
        generate_local_completion("prompt", model_path=model_dir)
    assert "is not a file" in str(excinfo.value)


def test_generate_local_completion_handles_missing_choices(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    model_path = tmp_path / "model.gguf"
    model_path.write_bytes(b"model")
    monkeypatch.setenv("GABRIEL_MODEL_PATH", str(model_path))

    class Stub:
        def __call__(self, *args: object, **kwargs: object) -> dict[str, object]:
            return {}

    monkeypatch.setattr("gabriel.inference._load_llama_model", lambda *a, **k: Stub())

    with pytest.raises(InferenceError) as excinfo:
        generate_local_completion("prompt")
    assert "did not return any choices" in str(excinfo.value)


def test_generate_local_completion_handles_non_string_text(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    model_path = tmp_path / "model.gguf"
    model_path.write_bytes(b"model")
    monkeypatch.setenv("GABRIEL_MODEL_PATH", str(model_path))

    class Stub:
        def __call__(self, *args: object, **kwargs: object) -> dict[str, object]:
            return {"choices": [{"text": 123}, {}]}

    monkeypatch.setattr("gabriel.inference._load_llama_model", lambda *a, **k: Stub())

    with pytest.raises(InferenceError) as excinfo:
        generate_local_completion("prompt")
    assert "empty text choices" in str(excinfo.value)


def test_generate_local_completion_accepts_explicit_model_path(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    model_path = tmp_path / "model.gguf"
    model_path.write_bytes(b"stub")

    class Stub:
        def __call__(self, *args: object, **kwargs: object) -> dict[str, object]:
            return {"choices": [{"text": " ok"}, "skip-me"]}

    monkeypatch.delenv("GABRIEL_MODEL_PATH", raising=False)
    monkeypatch.setattr("gabriel.inference._load_llama_model", lambda *a, **k: Stub())

    result = generate_local_completion("prompt", model_path=model_path)
    assert result.text == "ok"
    assert result.metadata["model_path"].endswith("model.gguf")


def test_generate_relay_completion_wraps_client(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    class StubCompletion:
        text = "relay result"
        model = "llama3"
        usage: dict[str, int] = {"prompt_tokens": 12, "completion_tokens": 8}

    class StubClient:
        def __init__(
            self, base_url: str, api_key: str | None = None, timeout: float = 10.0
        ) -> None:
            captured["base_url"] = base_url
            captured["api_key"] = api_key
            captured["timeout"] = timeout

        def infer(
            self,
            prompt: str,
            *,
            model: str | None = None,
            temperature: float | None = None,
            metadata: dict[str, object] | None = None,
        ) -> StubCompletion:
            captured["prompt"] = prompt
            captured["model"] = model
            captured["temperature"] = temperature
            captured["metadata"] = metadata
            return StubCompletion()

    monkeypatch.setattr("gabriel.inference.TokenPlaceClient", StubClient)

    result = generate_relay_completion(
        "Summarize alerts",
        base_url="https://relay.example",
        api_key="relay-token-placeholder",  # pragma: allowlist secret
        model="llama3-70b",
        temperature=0.6,
        metadata={"source": "unit-test"},
        timeout=20.0,
    )

    assert result.mode == "relay"
    assert result.text == "relay result"
    assert result.metadata["model"] == "llama3"
    assert result.metadata["requested_model"] == "llama3-70b"
    assert result.metadata["base_url"] == "https://relay.example"
    assert captured["prompt"] == "Summarize alerts"
    assert captured["metadata"] == {"source": "unit-test"}


def test_generate_relay_completion_handles_optional_metadata(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class StubCompletion:
        text = "relay text"
        model = "mistral"
        usage: dict[str, int] = {}

    class StubClient:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def infer(self, *args: object, **kwargs: object) -> StubCompletion:
            return StubCompletion()

    monkeypatch.setattr("gabriel.inference.TokenPlaceClient", StubClient)

    result = generate_relay_completion("prompt", base_url="https://relay.local")
    assert "metadata" not in result.metadata
    assert "requested_model" not in result.metadata


def test_generate_relay_completion_wraps_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    from gabriel.notify.tokenplace import TokenPlaceError

    class BrokenClient:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def infer(self, *args: object, **kwargs: object) -> None:
            raise TokenPlaceError("boom")

    monkeypatch.setattr("gabriel.inference.TokenPlaceClient", BrokenClient)

    with pytest.raises(InferenceError) as excinfo:
        generate_relay_completion("hi", base_url="https://relay")
    assert "boom" in str(excinfo.value)


def test_parse_metadata_validates_json() -> None:
    assert parse_metadata(None) is None
    assert parse_metadata("   ") is None
    assert parse_metadata('{"source": "demo"}') == {"source": "demo"}
    with pytest.raises(InferenceError):
        parse_metadata("not-json")
    with pytest.raises(InferenceError):
        parse_metadata("[1, 2, 3]")


def test_run_inference_local_branch(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    model_path = tmp_path / "model.gguf"
    model_path.write_bytes(b"stub")

    class Stub:
        def __call__(self, *args: object, **kwargs: object) -> dict[str, object]:
            return {"choices": [{"text": " done"}]}

    monkeypatch.setattr("gabriel.inference._load_llama_model", lambda *a, **k: Stub())
    result = run_inference("prompt", mode="local", model_path=model_path)
    assert result.mode == "local"
    assert result.text == "done"


def test_run_inference_relay_branch(monkeypatch: pytest.MonkeyPatch) -> None:
    class StubCompletion:
        text = "relay"
        model = "demo"
        usage: dict[str, int] = {}

    class StubClient:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def infer(self, *args: object, **kwargs: object) -> StubCompletion:
            return StubCompletion()

    monkeypatch.setattr("gabriel.inference.TokenPlaceClient", StubClient)
    result = run_inference("prompt", mode="relay", base_url="https://relay.local")
    assert result.mode == "relay"
    assert result.text == "relay"


def test_run_inference_rejects_unknown_mode() -> None:
    with pytest.raises(InferenceError):
        run_inference(
            "prompt",
            mode=cast(Literal["local", "relay"], "unsupported"),
        )


def test_load_llama_model_accepts_thread_override(monkeypatch: pytest.MonkeyPatch) -> None:
    class StubLlama:
        def __init__(self, **kwargs: object) -> None:
            self.kwargs = kwargs

    stub_module = SimpleNamespace(Llama=StubLlama)
    monkeypatch.setitem(sys.modules, "llama_cpp", stub_module)
    reset_local_model_cache()
    llama = _load_llama_model("/tmp/model.gguf", n_ctx=2048, n_threads=3)
    assert isinstance(llama, StubLlama)
    assert llama.kwargs == {"model_path": "/tmp/model.gguf", "n_ctx": 2048, "n_threads": 3}
    reset_local_model_cache()
    llama_default = _load_llama_model("/tmp/model.gguf", n_ctx=1024, n_threads=None)
    assert llama_default.kwargs == {"model_path": "/tmp/model.gguf", "n_ctx": 1024}
    reset_local_model_cache()
