from __future__ import annotations

import io
import os
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest

from gabriel.inference import InferenceError, InferenceResult
from gabriel.ui import cli


def test_cli_infer_local_mode_defaults_to_local(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    prompt = "Audit logs"
    model_path = tmp_path / "model.gguf"
    model_path.write_bytes(b"0")

    captured_kwargs: dict[str, Any] = {}

    def fake_run_inference(
        prompt_value: str,
        *,
        mode: str,
        **kwargs: Any,
    ) -> InferenceResult:
        captured_kwargs["prompt"] = prompt_value
        captured_kwargs["mode"] = mode
        captured_kwargs["kwargs"] = kwargs
        return InferenceResult(text="Local OK", mode="local", metadata={})

    monkeypatch.setattr(cli, "run_inference", fake_run_inference)
    monkeypatch.setenv("GABRIEL_MODEL_PATH", str(model_path))

    cli.main(["infer", "--model-path", str(model_path), "--max-tokens", "128", prompt])

    out = capsys.readouterr().out.strip()
    assert out == "Local OK"
    assert captured_kwargs["prompt"] == prompt
    assert captured_kwargs["mode"] == "local"
    kwargs = cast(dict[str, Any], captured_kwargs["kwargs"])
    assert kwargs["model_path"] == Path(model_path)
    assert kwargs["max_tokens"] == 128
    assert kwargs["temperature"] == cli.DEFAULT_LOCAL_TEMPERATURE


def test_cli_infer_relay_mode_requires_url(monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(SystemExit) as excinfo:
        cli.main(["infer", "--mode", "relay", "Check"])
    assert "--relay-url" in str(excinfo.value)


def test_cli_infer_relay_mode(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    captured_kwargs: dict[str, Any] = {}

    def fake_run_inference(
        prompt_value: str,
        *,
        mode: str,
        **kwargs: Any,
    ) -> InferenceResult:
        captured_kwargs["prompt"] = prompt_value
        captured_kwargs["mode"] = mode
        captured_kwargs["kwargs"] = kwargs
        return InferenceResult(text="Relay OK", mode="relay", metadata={})

    monkeypatch.delenv("GABRIEL_MODEL_PATH", raising=False)
    monkeypatch.setattr(cli, "run_inference", fake_run_inference)

    cli.main(
        [
            "infer",
            "--relay-url",
            "https://relay.local",
            "--api-key",
            "relay-token-placeholder",  # pragma: allowlist secret
            "--model",
            "llama3-8b",
            "--temperature",
            "0.7",
            "--metadata",
            '{"source": "unit"}',
            "--timeout",
            "5",
            "Summaries",
        ]
    )

    out = capsys.readouterr().out.strip()
    assert out == "Relay OK"
    assert captured_kwargs["mode"] == "relay"
    kwargs = cast(dict[str, Any], captured_kwargs["kwargs"])
    assert kwargs["base_url"] == "https://relay.local"
    assert kwargs["api_key"] == "relay-token-placeholder"  # pragma: allowlist secret
    assert kwargs["model"] == "llama3-8b"
    assert kwargs["temperature"] == 0.7
    assert kwargs["metadata"] == {"source": "unit"}
    assert kwargs["timeout"] == 5.0


def test_cli_infer_metadata_validation(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GABRIEL_MODEL_PATH", os.devnull)
    with pytest.raises(SystemExit) as excinfo:
        cli.main(
            [
                "infer",
                "--mode",
                "relay",
                "--relay-url",
                "https://relay.local",
                "--metadata",
                "not-json",
                "Prompt",
            ]
        )
    assert "Metadata must" in str(excinfo.value)


def test_cli_infer_reads_prompt_from_stdin(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GABRIEL_MODEL_PATH", raising=False)

    def fail_run(*args: object, **kwargs: object) -> InferenceResult:
        raise AssertionError("run_inference should not be called")

    monkeypatch.setattr(cli, "run_inference", fail_run)
    monkeypatch.setattr(cli.sys, "stdin", io.StringIO(""))
    with pytest.raises(SystemExit) as excinfo:
        cli.main(["infer", "--relay-url", "https://relay.local"])
    assert "Prompt text is required" in str(excinfo.value)


def test_cli_infer_local_mode_surfaces_errors(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    model_path = tmp_path / "model.gguf"
    model_path.write_bytes(b"0")

    def raise_error(*args: object, **kwargs: object) -> InferenceResult:
        raise InferenceError("local boom")

    monkeypatch.setattr(cli, "run_inference", raise_error)
    with pytest.raises(SystemExit) as excinfo:
        cli.main(["infer", "--mode", "local", "--model-path", str(model_path), "Prompt"])
    assert "local boom" in str(excinfo.value)


def test_cli_infer_relay_mode_surfaces_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    def raise_error(*args: object, **kwargs: object) -> InferenceResult:
        raise InferenceError("relay boom")

    monkeypatch.setattr(cli, "run_inference", raise_error)
    with pytest.raises(SystemExit) as excinfo:
        cli.main(["infer", "--mode", "relay", "--relay-url", "https://relay.local", "Prompt"])
    assert "relay boom" in str(excinfo.value)


def test_cli_infer_rejects_unsupported_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    namespace = SimpleNamespace(
        command="infer",
        prompt="prompt",
        mode="other",
        model_path=None,
        max_tokens=cli.DEFAULT_LOCAL_MAX_TOKENS,
        temperature=None,
        top_p=cli.DEFAULT_LOCAL_TOP_P,
        n_ctx=cli.DEFAULT_LOCAL_CONTEXT,
        n_threads=None,
        relay_url=None,
        api_key=None,
        relay_model=None,
        metadata=None,
        timeout=10.0,
    )

    monkeypatch.setattr(
        cli.argparse.ArgumentParser, "parse_args", lambda self, argv=None: namespace
    )
    with pytest.raises(SystemExit) as excinfo:
        cli.main([])
    assert "Unsupported inference mode" in str(excinfo.value)
