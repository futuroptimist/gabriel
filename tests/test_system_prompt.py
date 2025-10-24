"""Tests for the signed system prompt loader."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from gabriel.prompts import (
    DEFAULT_PROVENANCE_PATH,
    DEFAULT_SYSTEM_PROMPT_PATH,
    PromptProvenanceError,
    load_system_prompt,
    validate_provenance,
)


def test_load_system_prompt_success() -> None:
    """Loading the default prompt returns the expected text after validation."""

    prompt = load_system_prompt()
    assert "Gabriel" in prompt
    assert "privacy" in prompt.lower()


def test_load_system_prompt_digest_mismatch(tmp_path: Path) -> None:
    """Digest mismatches in the provenance metadata raise an error."""

    prompt_copy = tmp_path / "system.md"
    provenance_copy = tmp_path / "system.provenance.json"
    prompt_copy.write_text(DEFAULT_SYSTEM_PROMPT_PATH.read_text(encoding="utf-8"))
    provenance_payload = json.loads(DEFAULT_PROVENANCE_PATH.read_text(encoding="utf-8"))
    provenance_payload["subject"][0]["name"] = prompt_copy.name
    provenance_copy.write_text(json.dumps(provenance_payload), encoding="utf-8")

    prompt_copy.write_text(prompt_copy.read_text(encoding="utf-8") + "\nTampered")

    with pytest.raises(PromptProvenanceError):
        load_system_prompt(prompt_copy, provenance_copy)


def test_load_system_prompt_missing_file(tmp_path: Path) -> None:
    """Absent prompt files raise a provenance error."""

    missing_prompt = tmp_path / "missing.md"
    provenance_copy = tmp_path / "system.provenance.json"
    provenance_copy.write_text(DEFAULT_PROVENANCE_PATH.read_text(encoding="utf-8"))

    with pytest.raises(PromptProvenanceError):
        load_system_prompt(missing_prompt, provenance_copy)


def test_validate_provenance_requires_subject(tmp_path: Path) -> None:
    """Subject entries are required by the provenance document."""

    prompt_copy = tmp_path / "system.md"
    provenance_copy = tmp_path / "system.provenance.json"
    prompt_copy.write_text(DEFAULT_SYSTEM_PROMPT_PATH.read_text(encoding="utf-8"))

    provenance_payload = json.loads(DEFAULT_PROVENANCE_PATH.read_text(encoding="utf-8"))
    provenance_payload["subject"][0]["name"] = prompt_copy.name
    provenance_payload["subject"] = []
    provenance_copy.write_text(json.dumps(provenance_payload), encoding="utf-8")

    with pytest.raises(PromptProvenanceError):
        validate_provenance(prompt_copy, provenance_copy)


def test_validate_provenance_requires_matching_subject(tmp_path: Path) -> None:
    """The provenance subject must reference the actual prompt path."""

    prompt_copy = tmp_path / "system.md"
    provenance_copy = tmp_path / "system.provenance.json"
    prompt_copy.write_text(DEFAULT_SYSTEM_PROMPT_PATH.read_text(encoding="utf-8"))
    provenance_copy.write_text(DEFAULT_PROVENANCE_PATH.read_text(encoding="utf-8"))

    with pytest.raises(PromptProvenanceError):
        validate_provenance(prompt_copy, provenance_copy)


def test_validate_provenance_missing_digest(tmp_path: Path) -> None:
    """Subjects must define a sha256 digest."""

    prompt_copy = tmp_path / "system.md"
    provenance_copy = tmp_path / "system.provenance.json"
    prompt_copy.write_text(DEFAULT_SYSTEM_PROMPT_PATH.read_text(encoding="utf-8"))

    payload = json.loads(DEFAULT_PROVENANCE_PATH.read_text(encoding="utf-8"))
    payload["subject"][0]["name"] = prompt_copy.name
    payload["subject"][0].pop("digest", None)
    provenance_copy.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(PromptProvenanceError):
        validate_provenance(prompt_copy, provenance_copy)


def test_validate_provenance_invalid_predicate_type(tmp_path: Path) -> None:
    """predicateType must match the SLSA v1 identifier."""

    prompt_copy = tmp_path / "system.md"
    provenance_copy = tmp_path / "system.provenance.json"
    prompt_copy.write_text(DEFAULT_SYSTEM_PROMPT_PATH.read_text(encoding="utf-8"))

    payload = json.loads(DEFAULT_PROVENANCE_PATH.read_text(encoding="utf-8"))
    payload["subject"][0]["name"] = prompt_copy.name
    payload["predicateType"] = "https://example.invalid/provenance"
    provenance_copy.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(PromptProvenanceError):
        validate_provenance(prompt_copy, provenance_copy)


def test_validate_provenance_invalid_statement_type(tmp_path: Path) -> None:
    """_type must match the in-toto statement schema."""

    prompt_copy = tmp_path / "system.md"
    provenance_copy = tmp_path / "system.provenance.json"
    prompt_copy.write_text(DEFAULT_SYSTEM_PROMPT_PATH.read_text(encoding="utf-8"))

    payload = json.loads(DEFAULT_PROVENANCE_PATH.read_text(encoding="utf-8"))
    payload["subject"][0]["name"] = prompt_copy.name
    payload["_type"] = "https://example.invalid/Statement/v9"
    provenance_copy.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(PromptProvenanceError):
        validate_provenance(prompt_copy, provenance_copy)


def test_validate_provenance_invalid_json(tmp_path: Path) -> None:
    """Provenance documents must be valid JSON payloads."""

    prompt_copy = tmp_path / "system.md"
    provenance_copy = tmp_path / "system.provenance.json"
    prompt_copy.write_text(DEFAULT_SYSTEM_PROMPT_PATH.read_text(encoding="utf-8"))
    provenance_copy.write_text("{not-json", encoding="utf-8")

    with pytest.raises(PromptProvenanceError):
        validate_provenance(prompt_copy, provenance_copy)


def test_validate_provenance_requires_mapping(tmp_path: Path) -> None:
    """The provenance root must be a JSON mapping."""

    prompt_copy = tmp_path / "system.md"
    provenance_copy = tmp_path / "system.provenance.json"
    prompt_copy.write_text(DEFAULT_SYSTEM_PROMPT_PATH.read_text(encoding="utf-8"))
    provenance_copy.write_text(json.dumps(["invalid"]), encoding="utf-8")

    with pytest.raises(PromptProvenanceError):
        validate_provenance(prompt_copy, provenance_copy)


def test_validate_provenance_skips_non_dict_subjects(tmp_path: Path) -> None:
    """Non-dictionary subject entries are ignored while searching for the prompt."""

    prompt_copy = tmp_path / "system.md"
    provenance_copy = tmp_path / "system.provenance.json"
    prompt_copy.write_text(DEFAULT_SYSTEM_PROMPT_PATH.read_text(encoding="utf-8"))

    payload = json.loads(DEFAULT_PROVENANCE_PATH.read_text(encoding="utf-8"))
    digest = payload["subject"][0]["digest"]
    payload["subject"] = [
        "nonsense",
        {"name": prompt_copy.name, "digest": digest},
    ]
    provenance_copy.write_text(json.dumps(payload), encoding="utf-8")

    validated = validate_provenance(prompt_copy, provenance_copy)
    assert validated["subject"][1]["digest"] == digest
