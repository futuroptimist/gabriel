"""Helpers for verifying signed system prompt provenance."""

from __future__ import annotations

import base64
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

DEFAULT_PROMPT_PATH = Path("config/prompts/system.md")
DEFAULT_ATTESTATION_PATH = Path("config/prompts/system.attestation.json")
DEFAULT_PUBLIC_KEY_PATH = Path("config/prompts/system.pub")
EXPECTED_PAYLOAD_TYPE = "application/vnd.in-toto+json"


class ProvenanceVerificationError(RuntimeError):
    """Raised when a provenance statement fails verification."""


@dataclass(frozen=True)
class ProvenanceStatement:
    """Relevant metadata extracted from a provenance statement."""

    subject_name: str
    digest_sha256: str
    predicate_type: str
    builder_id: str


@dataclass(frozen=True)
class SignedPrompt:
    """A system prompt validated against a provenance attestation."""

    text: str
    path: Path
    provenance: ProvenanceStatement


def _pre_auth_encode(payload_type: str, payload: bytes) -> bytes:
    payload_type_bytes = payload_type.encode("utf-8")
    components = [
        b"DSSEv1",
        str(len(payload_type_bytes)).encode("ascii"),
        payload_type_bytes,
        str(len(payload)).encode("ascii"),
        payload,
    ]
    return b" ".join(components)


def _load_public_key(public_key_path: Path) -> Ed25519PublicKey:
    try:
        encoded = public_key_path.read_text(encoding="utf-8").strip()
    except FileNotFoundError as exc:
        raise ProvenanceVerificationError(
            f"public key file does not exist: {public_key_path}"
        ) from exc

    try:
        raw_bytes = base64.b64decode(encoded, validate=True)
    except (ValueError, TypeError) as exc:
        raise ProvenanceVerificationError("public key is not base64-encoded") from exc

    if len(raw_bytes) != 32:
        raise ProvenanceVerificationError("public key must contain 32 raw bytes")

    return Ed25519PublicKey.from_public_bytes(raw_bytes)


def _decode_envelope(attestation_path: Path) -> dict[str, Any]:
    try:
        data = attestation_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ProvenanceVerificationError(
            f"attestation file does not exist: {attestation_path}"
        ) from exc

    try:
        return json.loads(data)
    except json.JSONDecodeError as exc:
        raise ProvenanceVerificationError("attestation file is not valid JSON") from exc


def _decode_payload(envelope: dict[str, Any]) -> bytes:
    payload = envelope.get("payload")
    if not isinstance(payload, str):
        raise ProvenanceVerificationError("attestation payload must be a base64 string")

    try:
        return base64.b64decode(payload, validate=True)
    except (ValueError, TypeError) as exc:
        raise ProvenanceVerificationError("attestation payload is not valid base64") from exc


def _extract_subject(statement: dict[str, Any]) -> tuple[str, str]:
    subjects = statement.get("subject")
    if not isinstance(subjects, list) or not subjects:
        raise ProvenanceVerificationError("provenance subject list is empty")

    subject = subjects[0]
    if not isinstance(subject, dict):
        raise ProvenanceVerificationError("provenance subject entry must be an object")

    name = subject.get("name")
    digest = subject.get("digest", {})
    if not isinstance(name, str):
        raise ProvenanceVerificationError("provenance subject is missing a name")
    if not isinstance(digest, dict):
        raise ProvenanceVerificationError("provenance digest block must be an object")

    digest_sha256 = digest.get("sha256")
    if not isinstance(digest_sha256, str):
        raise ProvenanceVerificationError("provenance digest is missing a sha256 hash")

    return name, digest_sha256


def _builder_id(statement: dict[str, Any]) -> str:
    predicate = statement.get("predicate", {})
    if not isinstance(predicate, dict):
        raise ProvenanceVerificationError("provenance predicate must be an object")

    run_details = predicate.get("runDetails", {})
    if not isinstance(run_details, dict):
        raise ProvenanceVerificationError("provenance runDetails must be an object")

    builder = run_details.get("builder", {})
    if not isinstance(builder, dict):
        raise ProvenanceVerificationError("provenance builder metadata must be an object")

    builder_id = builder.get("id")
    if not isinstance(builder_id, str) or not builder_id.strip():
        raise ProvenanceVerificationError("builder id is missing")

    return builder_id


def verify_prompt_attestation(
    prompt_path: Path, attestation_path: Path, public_key_path: Path
) -> ProvenanceStatement:
    """Verify a DSSE-wrapped provenance statement for the provided prompt."""

    if not prompt_path.is_file():
        raise ProvenanceVerificationError(f"prompt file does not exist: {prompt_path}")

    envelope = _decode_envelope(attestation_path)

    payload_type = envelope.get("payloadType")
    if payload_type != EXPECTED_PAYLOAD_TYPE:
        raise ProvenanceVerificationError(
            f"unexpected payload type: {payload_type!r}"
        )

    payload_bytes = _decode_payload(envelope)

    signatures = envelope.get("signatures")
    if not isinstance(signatures, list) or not signatures:
        raise ProvenanceVerificationError("attestation must include at least one signature")

    signature_entry = signatures[0]
    if not isinstance(signature_entry, dict):
        raise ProvenanceVerificationError("signature entry must be an object")

    signature = signature_entry.get("sig")
    if not isinstance(signature, str):
        raise ProvenanceVerificationError("signature must be a base64-encoded string")

    try:
        signature_bytes = base64.b64decode(signature, validate=True)
    except (ValueError, TypeError) as exc:
        raise ProvenanceVerificationError("signature is not valid base64") from exc

    public_key = _load_public_key(public_key_path)

    try:
        public_key.verify(signature_bytes, _pre_auth_encode(payload_type, payload_bytes))
    except InvalidSignature as exc:
        raise ProvenanceVerificationError("signature verification failed") from exc

    try:
        payload_text = payload_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ProvenanceVerificationError("attestation payload is not valid UTF-8") from exc

    try:
        statement = json.loads(payload_text)
    except json.JSONDecodeError as exc:
        raise ProvenanceVerificationError("attestation payload is not valid JSON") from exc

    subject_name, digest_sha256 = _extract_subject(statement)

    prompt_digest = hashlib.sha256(prompt_path.read_bytes()).hexdigest()
    if prompt_digest != digest_sha256:
        raise ProvenanceVerificationError("prompt digest does not match provenance")

    predicate_type = statement.get("predicateType")
    if not isinstance(predicate_type, str):
        raise ProvenanceVerificationError("predicateType is missing from provenance")

    builder_id = _builder_id(statement)

    return ProvenanceStatement(
        subject_name=subject_name,
        digest_sha256=digest_sha256,
        predicate_type=predicate_type,
        builder_id=builder_id,
    )


def load_signed_system_prompt(base_path: Path | None = None) -> SignedPrompt:
    """Load the bundled system prompt after validating provenance."""

    root = base_path or Path(__file__).resolve().parents[2]
    prompt_path = root / DEFAULT_PROMPT_PATH
    attestation_path = root / DEFAULT_ATTESTATION_PATH
    public_key_path = root / DEFAULT_PUBLIC_KEY_PATH

    provenance = verify_prompt_attestation(prompt_path, attestation_path, public_key_path)
    prompt_text = prompt_path.read_text(encoding="utf-8")

    return SignedPrompt(text=prompt_text, path=prompt_path, provenance=provenance)


__all__ = [
    "DEFAULT_ATTESTATION_PATH",
    "DEFAULT_PROMPT_PATH",
    "DEFAULT_PUBLIC_KEY_PATH",
    "EXPECTED_PAYLOAD_TYPE",
    "ProvenanceStatement",
    "ProvenanceVerificationError",
    "SignedPrompt",
    "load_signed_system_prompt",
    "verify_prompt_attestation",
]
