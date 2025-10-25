"""Load and validate the repository's default system prompt."""

from __future__ import annotations

import hashlib
import json
from contextlib import ExitStack
from importlib import resources
from importlib.resources.abc import Traversable
from pathlib import Path
from typing import Any

__all__ = [
    "DEFAULT_SYSTEM_PROMPT_PATH",
    "DEFAULT_PROVENANCE_PATH",
    "PromptProvenanceError",
    "load_system_prompt",
    "validate_provenance",
]

_PROMPT_RESOURCES = resources.files("gabriel").joinpath("config", "prompts")
DEFAULT_SYSTEM_PROMPT_PATH = _PROMPT_RESOURCES.joinpath("system.md")
DEFAULT_PROVENANCE_PATH = _PROMPT_RESOURCES.joinpath("system.provenance.json")
_PACKAGE_ROOT = Path(__file__).resolve().parents[1]
_DEFAULT_PROMPT_CANONICAL_NAME = "config/prompts/system.md"


class PromptProvenanceError(RuntimeError):
    """Raised when the system prompt fails provenance validation."""


def load_system_prompt(
    prompt_path: Path | str | Traversable | None = None,
    provenance_path: Path | str | Traversable | None = None,
) -> str:
    """Return the system prompt after validating its provenance metadata."""

    with ExitStack() as stack:
        prompt, canonical_name, is_default_prompt = _resolve_prompt_path(prompt_path, stack)
        provenance = _resolve_provenance_path(
            provenance_path,
            prompt,
            stack,
            use_default_prompt=is_default_prompt,
        )

        if not prompt.is_file():
            raise PromptProvenanceError(f"System prompt file not found: {prompt}")

        _validate_provenance_resolved(prompt, provenance, canonical_name)
        contents = prompt.read_text(encoding="utf-8")
    return contents


def validate_provenance(
    prompt_path: Path | str | Traversable | None = None,
    provenance_path: Path | str | Traversable | None = None,
    *,
    canonical_name: str | None = None,
) -> dict[str, Any]:
    """Validate the provenance document for ``prompt_path`` and return its payload."""

    with ExitStack() as stack:
        prompt, default_canonical, is_default_prompt = _resolve_prompt_path(prompt_path, stack)
        canonical_hint = canonical_name or default_canonical
        provenance = _resolve_provenance_path(
            provenance_path,
            prompt,
            stack,
            use_default_prompt=is_default_prompt,
        )

        payload = _validate_provenance_resolved(prompt, provenance, canonical_hint)
    return payload


def _resolve_prompt_path(
    value: Path | str | Traversable | None,
    stack: ExitStack,
) -> tuple[Path, str | None, bool]:
    if value is None or (isinstance(value, Traversable) and value == DEFAULT_SYSTEM_PROMPT_PATH):
        path = stack.enter_context(resources.as_file(DEFAULT_SYSTEM_PROMPT_PATH))
        return Path(path), _DEFAULT_PROMPT_CANONICAL_NAME, True
    assert value is not None
    return _coerce_path(value, stack), None, False


def _resolve_provenance_path(
    value: Path | str | Traversable | None,
    prompt: Path,
    stack: ExitStack,
    *,
    use_default_prompt: bool,
) -> Path:
    if value is None:
        if use_default_prompt:
            path = stack.enter_context(resources.as_file(DEFAULT_PROVENANCE_PATH))
            return Path(path)
        return _derive_provenance_path(prompt)
    return _coerce_path(value, stack)


def _coerce_path(value: Path | str | Traversable, stack: ExitStack) -> Path:
    if isinstance(value, Traversable):
        path = stack.enter_context(resources.as_file(value))
        return Path(path)
    return Path(value)


def _validate_provenance_resolved(
    prompt: Path, provenance: Path, canonical_name: str | None
) -> dict[str, Any]:
    payload = _load_provenance_document(provenance)
    subjects = payload.get("subject")
    if not isinstance(subjects, list) or not subjects:
        raise PromptProvenanceError("Provenance document is missing subject entries")

    subject = _match_subject(subjects, prompt, canonical_name)
    digest_section = subject.get("digest") if isinstance(subject, dict) else None
    if not isinstance(digest_section, dict) or "sha256" not in digest_section:
        raise PromptProvenanceError("Provenance subject is missing a sha256 digest")

    expected_digest = str(digest_section["sha256"]).lower()
    actual_digest = hashlib.sha256(prompt.read_bytes()).hexdigest()
    if expected_digest != actual_digest:
        raise PromptProvenanceError("System prompt digest mismatch; provenance validation failed")

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


def _match_subject(
    subjects: list[Any], prompt_path: Path, canonical_name: str | None
) -> dict[str, Any]:
    expected_names = _candidate_subject_names(prompt_path, canonical_name)
    for entry in subjects:
        if not isinstance(entry, dict):
            continue
        name = entry.get("name")
        if isinstance(name, str) and name in expected_names:
            return entry
    raise PromptProvenanceError("Provenance document does not describe the system prompt file")


def _candidate_subject_names(prompt_path: Path, canonical_name: str | None) -> set[str]:
    candidates = {prompt_path.name, str(prompt_path)}
    if canonical_name:
        candidates.add(canonical_name)
    try:
        relative = prompt_path.relative_to(_PACKAGE_ROOT)
    except ValueError:
        pass
    else:
        candidates.add(str(relative))
    normalized = {candidate.replace("\\", "/") for candidate in candidates}
    return normalized
