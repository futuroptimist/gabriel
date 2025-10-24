"""Load and validate the repository's default system prompt."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

__all__ = [
    "DEFAULT_SYSTEM_PROMPT_PATH",
    "DEFAULT_PROVENANCE_PATH",
    "PromptProvenanceError",
    "load_system_prompt",
    "validate_provenance",
]

_REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SYSTEM_PROMPT_PATH = _REPO_ROOT / "config" / "prompts" / "system.md"
DEFAULT_PROVENANCE_PATH = (
    DEFAULT_SYSTEM_PROMPT_PATH.with_name(f"{DEFAULT_SYSTEM_PROMPT_PATH.stem}.provenance.json")
)


class PromptProvenanceError(RuntimeError):
    """Raised when the system prompt fails provenance validation."""


def load_system_prompt(
    prompt_path: Path | str | None = None,
    provenance_path: Path | str | None = None,
) -> str:
    """Return the system prompt after validating its provenance metadata."""

    prompt = Path(prompt_path) if prompt_path is not None else DEFAULT_SYSTEM_PROMPT_PATH
    provenance = (
        Path(provenance_path)
        if provenance_path is not None
        else _derive_provenance_path(prompt)
    )

    if not prompt.is_file():
        raise PromptProvenanceError(f"System prompt file not found: {prompt}")

    validate_provenance(prompt, provenance)
    return prompt.read_text(encoding="utf-8")


def validate_provenance(
    prompt_path: Path | str | None = None,
    provenance_path: Path | str | None = None,
) -> dict[str, Any]:
    """Validate the provenance document for ``prompt_path`` and return its payload."""

    prompt = Path(prompt_path) if prompt_path is not None else DEFAULT_SYSTEM_PROMPT_PATH
    provenance = (
        Path(provenance_path)
        if provenance_path is not None
        else _derive_provenance_path(prompt)
    )

    payload = _load_provenance_document(provenance)
    subjects = payload.get("subject")
    if not isinstance(subjects, list) or not subjects:
        raise PromptProvenanceError("Provenance document is missing subject entries")

    subject = _match_subject(subjects, prompt)
    digest_section = subject.get("digest") if isinstance(subject, dict) else None
    if not isinstance(digest_section, dict) or "sha256" not in digest_section:
        raise PromptProvenanceError("Provenance subject is missing a sha256 digest")

    expected_digest = str(digest_section["sha256"]).lower()
    actual_digest = hashlib.sha256(prompt.read_bytes()).hexdigest()
    if expected_digest != actual_digest:
        raise PromptProvenanceError(
            "System prompt digest mismatch; provenance validation failed"
        )

    predicate_type = payload.get("predicateType")
    if predicate_type != "https://slsa.dev/provenance/v1":
        raise PromptProvenanceError(
            "Unexpected predicateType in provenance document; expected SLSA v1"
        )

    statement_type = payload.get("_type")
    if statement_type != "https://in-toto.io/Statement/v1":
        raise PromptProvenanceError(
            "Invalid provenance statement type; expected in-toto Statement v1"
        )

    return payload


def _derive_provenance_path(prompt_path: Path) -> Path:
    return prompt_path.with_name(f"{prompt_path.stem}.provenance.json")


def _load_provenance_document(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:  # pragma: no cover - handled by tests indirectly
        raise PromptProvenanceError(f"Provenance file not found: {path}") from exc
    except OSError as exc:  # pragma: no cover - unlikely but defensive
        raise PromptProvenanceError(f"Failed to read provenance file {path}: {exc}") from exc

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise PromptProvenanceError(f"Provenance file {path} is not valid JSON: {exc}") from exc

    if not isinstance(payload, dict):
        raise PromptProvenanceError("Provenance document must be a JSON object")
    return payload


def _match_subject(subjects: list[Any], prompt_path: Path) -> dict[str, Any]:
    expected_names = _candidate_subject_names(prompt_path)
    for entry in subjects:
        if not isinstance(entry, dict):
            continue
        name = entry.get("name")
        if isinstance(name, str) and name in expected_names:
            return entry
    raise PromptProvenanceError(
        "Provenance document does not describe the system prompt file"
    )


def _candidate_subject_names(prompt_path: Path) -> set[str]:
    candidates = {prompt_path.name, str(prompt_path)}
    try:
        relative = prompt_path.relative_to(_REPO_ROOT)
    except ValueError:
        pass
    else:
        candidates.add(str(relative))
    normalized = {candidate.replace("\\", "/") for candidate in candidates}
    return normalized
