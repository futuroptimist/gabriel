"""Tests for the LLM policy validation utilities."""

from __future__ import annotations

import os
import stat
import subprocess  # nosec B404
from pathlib import Path

import pytest

from gabriel.policy import (
    PolicyValidationError,
    PolicyValidationResult,
    load_policy_document,
    validate_policy_document,
    validate_policy_file,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def _write_policy(tmp_path: Path, content: str) -> Path:
    path = tmp_path / "policy.yaml"
    path.write_text(content, encoding="utf-8")
    return path


def test_validate_policy_accepts_valid_document(tmp_path: Path) -> None:
    policy_path = _write_policy(
        tmp_path,
        """
commands:
  allow:
    - git status
    - git diff --stat
  deny:
    - curl http://*
validators:
  shell:
    arguments_regex: "^(git|npm|pytest)"
metadata:
  repo_name: gabriel
  sensitivity_level: standard
  allowed_domains:
    - example.com
  token_ttl_hours: 12
""",
    )
    result = validate_policy_file(policy_path)
    assert isinstance(result, PolicyValidationResult)
    assert result.is_valid
    assert not result.errors
    assert not result.warnings


def test_validate_policy_rejects_missing_commands() -> None:
    document = {
        "validators": {"shell": {"arguments_regex": "^git"}},
    }
    result = validate_policy_document(document)
    assert not result.is_valid
    assert "Missing required 'commands' section" in result.errors


def test_validate_policy_detects_duplicate_allow_entries() -> None:
    document = {
        "commands": {"allow": ["git status", "git status"], "deny": []},
        "validators": {"shell": {"arguments_regex": "^git"}},
    }
    result = validate_policy_document(document)
    assert not result.is_valid
    assert any("duplicate entry" in message for message in result.errors)


def test_validate_policy_requires_allow_or_deny_entries() -> None:
    document = {
        "commands": {"allow": [], "deny": []},
        "validators": {"shell": {"arguments_regex": "^git"}},
    }
    result = validate_policy_document(document)
    assert not result.is_valid
    assert any("at least one allow or deny" in message for message in result.errors)


def test_validate_policy_detects_overlapping_command_rules() -> None:
    document = {
        "commands": {"allow": ["git status"], "deny": ["git status"]},
        "validators": {"shell": {"arguments_regex": "^git"}},
    }
    result = validate_policy_document(document)
    assert not result.is_valid
    assert any("both allow and deny" in message for message in result.errors)


def test_validate_policy_flags_non_mapping_commands_section() -> None:
    document = {
        "commands": [],
        "validators": {"shell": {"arguments_regex": "^git"}},
    }
    result = validate_policy_document(document)
    assert not result.is_valid
    assert "must be a mapping" in result.errors[0]


def test_validate_policy_flags_invalid_command_entries() -> None:
    document = {
        "commands": {"allow": [123, ""], "deny": "curl"},
        "validators": {"shell": {"arguments_regex": "^git"}},
    }
    result = validate_policy_document(document)
    assert not result.is_valid
    messages = " ".join(result.errors)
    assert "commands.allow" in messages
    assert "commands.deny" in messages


def test_validate_policy_warns_on_extra_allow_commands(tmp_path: Path) -> None:
    policy_path = _write_policy(
        tmp_path,
        """
commands:
  allow:
    - git status
  deny:
    - curl http://*
validators:
  shell:
    arguments_regex: "^git"
metadata:
  extra_allow_commands:
    - git commit
""",
    )
    result = validate_policy_file(policy_path)
    assert result.is_valid
    assert result.warnings
    assert any("extra_allow_commands" in warning for warning in result.warnings)


def test_validate_policy_accepts_extra_allow_commands_in_allow_list(tmp_path: Path) -> None:
    policy_path = _write_policy(
        tmp_path,
        """
commands:
  allow:
    - git status
metadata:
  extra_allow_commands:
    - git status
validators:
  shell:
    arguments_regex: "^git"
""",
    )
    result = validate_policy_file(policy_path)
    assert result.is_valid
    assert not result.warnings


def test_validate_policy_flags_missing_validators() -> None:
    document = {
        "commands": {"allow": ["git status"]},
    }
    result = validate_policy_document(document)
    assert not result.is_valid
    assert "Missing required 'validators' section" in result.errors


def test_validate_policy_flags_non_mapping_validators_section() -> None:
    document = {
        "commands": {"allow": ["git status"]},
        "validators": [],
    }
    result = validate_policy_document(document)
    assert not result.is_valid
    assert any("must be a mapping" in message for message in result.errors)


def test_validate_policy_requires_at_least_one_validator() -> None:
    document = {
        "commands": {"allow": ["git status"]},
        "validators": {},
    }
    result = validate_policy_document(document)
    assert not result.is_valid
    assert any("At least one validator" in message for message in result.errors)


def test_validate_policy_flags_invalid_validator_names() -> None:
    document = {
        "commands": {"allow": ["git status"]},
        "validators": {"": {"arguments_regex": "^git"}},
    }
    result = validate_policy_document(document)
    assert not result.is_valid
    assert any("Validator names" in message for message in result.errors)


def test_validate_policy_flags_non_mapping_validator_settings() -> None:
    document = {
        "commands": {"allow": ["git status"]},
        "validators": {"shell": "^git"},
    }
    result = validate_policy_document(document)
    assert not result.is_valid
    assert any("must define a mapping" in message for message in result.errors)


def test_validate_policy_flags_invalid_regex_configuration() -> None:
    document = {
        "commands": {"allow": ["git status"]},
        "validators": {"shell": {"arguments_regex": "["}},
    }
    result = validate_policy_document(document)
    assert not result.is_valid
    assert any("not a valid regex" in message for message in result.errors)


def test_validate_policy_rejects_blank_regex_configuration() -> None:
    document = {
        "commands": {"allow": ["git status"]},
        "validators": {"shell": {"arguments_regex": "  "}},
    }
    result = validate_policy_document(document)
    assert not result.is_valid
    assert any("must be a non-empty string" in message for message in result.errors)


def test_validate_policy_rejects_unsupported_validator_value() -> None:
    sentinel = object()
    document = {
        "commands": {"allow": ["git status"]},
        "validators": {"shell": {"arguments_regex": "^git", "extra": sentinel}},
    }
    result = validate_policy_document(document)
    assert not result.is_valid
    assert any("unsupported value" in message for message in result.errors)


def test_validate_policy_accepts_supported_validator_values() -> None:
    document = {
        "commands": {"allow": ["git status"]},
        "validators": {
            "shell": {
                "arguments_regex": "^git",
                "env": ["CI"],
                "limits": {"max_calls": 5},
            }
        },
    }
    result = validate_policy_document(document)
    assert result.is_valid


def test_validate_policy_flags_metadata_errors() -> None:
    document = {
        "commands": {"allow": ["git status"]},
        "validators": {"shell": {"arguments_regex": "^git"}},
        "metadata": {
            "repo_name": 123,
            "sensitivity_level": 45,
            "allowed_domains": [""],
            "token_ttl_hours": -1,
            "extra_allow_commands": ["", "git deploy"],
        },
    }
    result = validate_policy_document(document)
    assert not result.is_valid
    messages = " ".join(result.errors)
    assert "repo_name" in messages
    assert "sensitivity_level" in messages
    assert "allowed_domains" in messages
    assert "token_ttl_hours" in messages
    assert "extra_allow_commands" in messages


def test_validate_policy_rejects_metadata_non_mapping() -> None:
    document = {
        "commands": {"allow": ["git status"]},
        "validators": {"shell": {"arguments_regex": "^git"}},
        "metadata": "invalid",
    }
    result = validate_policy_document(document)
    assert not result.is_valid
    assert any("must be a mapping" in message for message in result.errors)


def test_validate_policy_flags_unknown_metadata_keys() -> None:
    document = {
        "commands": {"allow": ["git status"]},
        "validators": {"shell": {"arguments_regex": "^git"}},
        "metadata": {"unexpected": "value"},
    }
    result = validate_policy_document(document)
    assert result.is_valid
    assert any("Unknown metadata key" in warning for warning in result.warnings)


def test_validate_policy_records_unexpected_top_level_keys() -> None:
    document = {
        "commands": {"allow": ["git status"]},
        "validators": {"shell": {"arguments_regex": "^git"}},
        "extra": {},
    }
    result = validate_policy_document(document)
    assert result.is_valid
    assert any("Unexpected top-level key" in warning for warning in result.warnings)


def test_validate_policy_rejects_empty_allowed_domains_list() -> None:
    document = {
        "commands": {"allow": ["git status"]},
        "validators": {"shell": {"arguments_regex": "^git"}},
        "metadata": {"allowed_domains": []},
    }
    result = validate_policy_document(document)
    assert not result.is_valid
    assert any("allowed_domains must be a non-empty list" in message for message in result.errors)


def test_validate_policy_rejects_non_numeric_ttl() -> None:
    document = {
        "commands": {"allow": ["git status"]},
        "validators": {"shell": {"arguments_regex": "^git"}},
        "metadata": {"token_ttl_hours": "fast"},
    }
    result = validate_policy_document(document)
    assert not result.is_valid
    assert any("must be a number" in message for message in result.errors)


def test_validate_policy_rejects_empty_extra_allow_commands() -> None:
    document = {
        "commands": {"allow": ["git status"]},
        "validators": {"shell": {"arguments_regex": "^git"}},
        "metadata": {"extra_allow_commands": []},
    }
    result = validate_policy_document(document)
    assert not result.is_valid
    assert any("must be a non-empty list" in message for message in result.errors)


def test_validate_policy_cli_succeeds_on_valid_policy(tmp_path: Path) -> None:
    policy_path = _write_policy(
        tmp_path,
        """
commands:
  allow:
    - git status
validators:
  shell:
    arguments_regex: "^git"
""",
    )
    script = REPO_ROOT / "scripts" / "validate_policy.py"
    result = subprocess.run(
        [str(script), str(policy_path)],
        check=False,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        env={**os.environ, "PYTHONPATH": str(REPO_ROOT)},
    )  # nosec B603 B607
    assert result.returncode == 0
    assert "OK:" in result.stdout
    assert not result.stderr


def test_validate_policy_cli_fails_on_invalid_policy(tmp_path: Path) -> None:
    policy_path = _write_policy(
        tmp_path,
        """
validators:
  shell:
    arguments_regex: "^git"
""",
    )
    script = REPO_ROOT / "scripts" / "validate_policy.py"
    result = subprocess.run(
        [str(script), str(policy_path)],
        check=False,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        env={**os.environ, "PYTHONPATH": str(REPO_ROOT)},
    )  # nosec B603 B607
    assert result.returncode == 1
    assert "ERROR" in result.stderr


def test_validate_policy_script_is_executable() -> None:
    script = REPO_ROOT / "scripts" / "validate_policy.py"
    assert script.exists()
    mode = script.stat().st_mode
    assert mode & stat.S_IXUSR


def test_load_policy_document_rejects_non_mapping(tmp_path: Path) -> None:
    policy_path = _write_policy(tmp_path, "- item")
    with pytest.raises(PolicyValidationError):
        load_policy_document(policy_path)
