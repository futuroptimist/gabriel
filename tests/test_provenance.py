"""Tests for signed prompt provenance verification."""

from __future__ import annotations

import base64
import json
from collections.abc import Callable
from pathlib import Path

import pytest

import gabriel.security.provenance as provenance
from gabriel.security import (
    DEFAULT_ATTESTATION_PATH,
    DEFAULT_PROMPT_PATH,
    DEFAULT_PUBLIC_KEY_PATH,
    ProvenanceVerificationError,
    load_signed_system_prompt,
    verify_prompt_attestation,
)


def _repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _copy_signed_prompt_tree(tmp_path: Path) -> None:
    root = _repository_root()
    for relative in (
        DEFAULT_PROMPT_PATH,
        DEFAULT_ATTESTATION_PATH,
        DEFAULT_PUBLIC_KEY_PATH,
    ):
        source = root / relative
        destination = tmp_path / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(source.read_bytes())


def _mutate_attestation_payload(attestation_path: Path, mutate: Callable[[dict[str, object]], None]) -> None:
    envelope = json.loads(attestation_path.read_text(encoding="utf-8"))
    payload = json.loads(base64.b64decode(envelope["payload"]))
    mutate(payload)
    envelope["payload"] = base64.b64encode(
        json.dumps(payload).encode("utf-8")
    ).decode("ascii")
    attestation_path.write_text(json.dumps(envelope), encoding="utf-8")


def _stub_public_key(monkeypatch: pytest.MonkeyPatch) -> None:
    class _StubKey:
        def verify(self, signature: bytes, data: bytes) -> None:  # noqa: ARG002
            return None

    def _load_public_key_stub(_: Path) -> _StubKey:
        return _StubKey()

    monkeypatch.setattr(provenance, "_load_public_key", _load_public_key_stub)


def test_verify_prompt_attestation_succeeds() -> None:
    """The provenance attestation validates the default system prompt."""

    root = _repository_root()
    result = verify_prompt_attestation(
        root / DEFAULT_PROMPT_PATH,
        root / DEFAULT_ATTESTATION_PATH,
        root / DEFAULT_PUBLIC_KEY_PATH,
    )

    assert result.subject_name == DEFAULT_PROMPT_PATH.as_posix()
    assert result.digest_sha256
    assert result.predicate_type == "https://slsa.dev/provenance/v1"
    assert result.builder_id == "urn:gabriel:prompt-signer"


def test_verify_prompt_attestation_rejects_modified_prompt(tmp_path: Path) -> None:
    """Changing the prompt contents triggers a digest mismatch error."""

    _copy_signed_prompt_tree(tmp_path)
    prompt_path = tmp_path / DEFAULT_PROMPT_PATH
    prompt_path.write_text(prompt_path.read_text(encoding="utf-8") + "\nTampered.", encoding="utf-8")

    with pytest.raises(ProvenanceVerificationError):
        verify_prompt_attestation(
            prompt_path,
            tmp_path / DEFAULT_ATTESTATION_PATH,
            tmp_path / DEFAULT_PUBLIC_KEY_PATH,
        )


def test_load_signed_system_prompt_validates_attestation() -> None:
    """``load_signed_system_prompt`` returns prompt text once provenance succeeds."""

    root = _repository_root()
    signed = load_signed_system_prompt(base_path=root)

    assert signed.path == root / DEFAULT_PROMPT_PATH
    assert "Gabriel" in signed.text
    assert signed.provenance.subject_name == DEFAULT_PROMPT_PATH.as_posix()


def test_verify_prompt_attestation_fails_when_attestation_missing(tmp_path: Path) -> None:
    """Missing attestation files trigger a verification error."""

    _copy_signed_prompt_tree(tmp_path)
    attestation_path = tmp_path / DEFAULT_ATTESTATION_PATH
    attestation_path.unlink()

    with pytest.raises(ProvenanceVerificationError):
        verify_prompt_attestation(
            tmp_path / DEFAULT_PROMPT_PATH,
            attestation_path,
            tmp_path / DEFAULT_PUBLIC_KEY_PATH,
        )


def test_verify_prompt_attestation_rejects_unexpected_payload_type(tmp_path: Path) -> None:
    """Attestations must advertise the expected DSSE payload type."""

    _copy_signed_prompt_tree(tmp_path)
    attestation_path = tmp_path / DEFAULT_ATTESTATION_PATH
    envelope = json.loads(attestation_path.read_text(encoding="utf-8"))
    envelope["payloadType"] = "application/example"
    attestation_path.write_text(json.dumps(envelope), encoding="utf-8")

    with pytest.raises(ProvenanceVerificationError):
        verify_prompt_attestation(
            tmp_path / DEFAULT_PROMPT_PATH,
            attestation_path,
            tmp_path / DEFAULT_PUBLIC_KEY_PATH,
        )


def test_verify_prompt_attestation_rejects_invalid_signature(tmp_path: Path) -> None:
    """A modified signature fails verification even when digests match."""

    _copy_signed_prompt_tree(tmp_path)
    attestation_path = tmp_path / DEFAULT_ATTESTATION_PATH
    envelope = json.loads(attestation_path.read_text(encoding="utf-8"))
    envelope["signatures"][0]["sig"] = "AAAA"
    attestation_path.write_text(json.dumps(envelope), encoding="utf-8")

    with pytest.raises(ProvenanceVerificationError):
        verify_prompt_attestation(
            tmp_path / DEFAULT_PROMPT_PATH,
            attestation_path,
            tmp_path / DEFAULT_PUBLIC_KEY_PATH,
        )


def test_verify_prompt_attestation_requires_string_signatures(tmp_path: Path) -> None:
    """Signature fields must be base64-encoded strings."""

    _copy_signed_prompt_tree(tmp_path)
    attestation_path = tmp_path / DEFAULT_ATTESTATION_PATH
    envelope = json.loads(attestation_path.read_text(encoding="utf-8"))
    envelope["signatures"][0]["sig"] = 123
    attestation_path.write_text(json.dumps(envelope), encoding="utf-8")

    with pytest.raises(ProvenanceVerificationError):
        verify_prompt_attestation(
            tmp_path / DEFAULT_PROMPT_PATH,
            attestation_path,
            tmp_path / DEFAULT_PUBLIC_KEY_PATH,
        )


def test_verify_prompt_attestation_rejects_malformed_payload(tmp_path: Path) -> None:
    """Payload must be valid base64 encoding a JSON statement."""

    _copy_signed_prompt_tree(tmp_path)
    attestation_path = tmp_path / DEFAULT_ATTESTATION_PATH
    envelope = json.loads(attestation_path.read_text(encoding="utf-8"))
    envelope["payload"] = "!@#"
    attestation_path.write_text(json.dumps(envelope), encoding="utf-8")

    with pytest.raises(ProvenanceVerificationError):
        verify_prompt_attestation(
            tmp_path / DEFAULT_PROMPT_PATH,
            attestation_path,
            tmp_path / DEFAULT_PUBLIC_KEY_PATH,
        )


def test_verify_prompt_attestation_rejects_empty_subject_list(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Attestations must describe at least one subject."""

    _copy_signed_prompt_tree(tmp_path)
    attestation_path = tmp_path / DEFAULT_ATTESTATION_PATH
    _mutate_attestation_payload(attestation_path, lambda payload: payload.update({"subject": []}))
    _stub_public_key(monkeypatch)

    with pytest.raises(ProvenanceVerificationError, match="subject list is empty"):
        verify_prompt_attestation(
            tmp_path / DEFAULT_PROMPT_PATH,
            attestation_path,
            tmp_path / DEFAULT_PUBLIC_KEY_PATH,
        )


def test_verify_prompt_attestation_requires_builder_metadata(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The provenance statement must include a builder identifier."""

    _copy_signed_prompt_tree(tmp_path)
    attestation_path = tmp_path / DEFAULT_ATTESTATION_PATH

    def remove_builder_id(payload: dict[str, object]) -> None:
        predicate = payload.setdefault("predicate", {})
        run_details = predicate.setdefault("runDetails", {})
        builder = run_details.setdefault("builder", {})
        builder["id"] = None

    _mutate_attestation_payload(attestation_path, remove_builder_id)
    _stub_public_key(monkeypatch)

    with pytest.raises(ProvenanceVerificationError, match="builder id is missing"):
        verify_prompt_attestation(
            tmp_path / DEFAULT_PROMPT_PATH,
            attestation_path,
            tmp_path / DEFAULT_PUBLIC_KEY_PATH,
        )
