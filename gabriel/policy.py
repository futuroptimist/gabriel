"""Utilities for validating LLM agent policy definitions."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class PolicyValidationError(RuntimeError):
    """Raised when a policy file cannot be loaded or violates required structure."""


@dataclass(frozen=True, slots=True)
class PolicyValidationResult:
    """Represents validation output for a policy document."""

    errors: tuple[str, ...]
    warnings: tuple[str, ...]

    @property
    def is_valid(self) -> bool:
        """Return ``True`` when the policy has no blocking errors."""

        return not self.errors


_ALLOWED_TOP_LEVEL_KEYS: frozenset[str] = frozenset({"commands", "validators", "metadata"})
_METADATA_ALLOWED_KEYS: frozenset[str] = frozenset(
    {
        "repo_name",
        "sensitivity_level",
        "allowed_domains",
        "token_ttl_hours",
        "extra_allow_commands",
    }
)
_SIMPLE_VALUE_TYPES = (str, int, float, bool)


def load_policy_document(path: Path | str) -> dict[str, Any]:
    """Return the parsed policy document from ``path``.

    Parameters
    ----------
    path:
        File system path pointing to the YAML policy definition.
    """

    policy_path = Path(path)
    try:
        raw = policy_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:  # pragma: no cover - exercised via tests
        raise PolicyValidationError(f"Policy file not found: {policy_path}") from exc

    try:
        document = yaml.safe_load(raw) or {}
    except yaml.YAMLError as exc:  # pragma: no cover - YAML parser exercised in tests
        raise PolicyValidationError(f"Failed to parse YAML in {policy_path}: {exc}") from exc

    if not isinstance(document, dict):
        raise PolicyValidationError("Policy root must be a mapping of sections to configuration")

    return document


def validate_policy_document(document: dict[str, Any]) -> PolicyValidationResult:
    """Validate a loaded policy document and return accumulated issues."""

    errors: list[str] = []
    warnings: list[str] = []

    for key in document:
        if key not in _ALLOWED_TOP_LEVEL_KEYS:
            warnings.append(f"Unexpected top-level key '{key}' will be ignored by templates")

    commands = document.get("commands")
    allow_commands: set[str] = set()
    deny_commands: set[str] = set()
    if commands is None:
        errors.append("Missing required 'commands' section")
    elif not isinstance(commands, dict):
        errors.append("'commands' section must be a mapping with allow/deny lists")
    else:
        _validate_command_list(commands, "allow", allow_commands, errors)
        _validate_command_list(commands, "deny", deny_commands, errors)
        if not allow_commands and not deny_commands:
            errors.append("'commands' must include at least one allow or deny entry")
        overlap = allow_commands & deny_commands
        if overlap:
            formatted = ", ".join(sorted(overlap))
            errors.append(f"Commands present in both allow and deny lists: {formatted}")

    validators = document.get("validators")
    if validators is None:
        errors.append("Missing required 'validators' section")
    elif not isinstance(validators, dict):
        errors.append("'validators' section must be a mapping of validator names to settings")
    elif not validators:
        errors.append("At least one validator configuration is required")
    else:
        for name, settings in validators.items():
            if not isinstance(name, str) or not name.strip():
                errors.append("Validator names must be non-empty strings")
                continue
            if not isinstance(settings, dict) or not settings:
                errors.append(f"Validator '{name}' must define a mapping of settings")
                continue
            for option, value in settings.items():
                if option == "arguments_regex":
                    _validate_regex(value, name, errors)
                    continue
                if not _is_supported_value(value):
                    errors.append(
                        f"Validator '{name}' option '{option}' has unsupported value {value!r}"
                    )

    metadata = document.get("metadata")
    if metadata is not None:
        if not isinstance(metadata, dict):
            errors.append("'metadata' section must be a mapping when provided")
        else:
            for key in metadata:
                if key not in _METADATA_ALLOWED_KEYS:
                    warnings.append(f"Unknown metadata key '{key}' will be ignored by templates")
            repo_name = metadata.get("repo_name")
            if repo_name is not None and not isinstance(repo_name, str):
                errors.append("metadata.repo_name must be a string when specified")
            sensitivity = metadata.get("sensitivity_level")
            if sensitivity is not None and not isinstance(sensitivity, str):
                errors.append("metadata.sensitivity_level must be a string when specified")
            allowed_domains = metadata.get("allowed_domains")
            if allowed_domains is not None:
                if not isinstance(allowed_domains, list) or not allowed_domains:
                    errors.append("metadata.allowed_domains must be a non-empty list of domains")
                elif not all(
                    isinstance(domain, str) and domain.strip() for domain in allowed_domains
                ):
                    errors.append("metadata.allowed_domains entries must be non-empty strings")
            ttl = metadata.get("token_ttl_hours")
            if ttl is not None:
                if not isinstance(ttl, int | float):
                    errors.append("metadata.token_ttl_hours must be a number when specified")
                elif ttl <= 0:
                    errors.append("metadata.token_ttl_hours must be greater than zero")
            extra_allow = metadata.get("extra_allow_commands")
            if extra_allow is not None:
                if not isinstance(extra_allow, list) or not extra_allow:
                    errors.append(
                        "metadata.extra_allow_commands must be a non-empty list when specified"
                    )
                elif not all(isinstance(item, str) and item.strip() for item in extra_allow):
                    errors.append("metadata.extra_allow_commands entries must be non-empty strings")
                else:
                    missing = sorted(
                        {item.strip() for item in extra_allow if item.strip() not in allow_commands}
                    )
                    if missing:
                        warnings.append(
                            "metadata.extra_allow_commands contains entries not present in "
                            f"commands.allow: {', '.join(missing)}"
                        )

    return PolicyValidationResult(errors=tuple(errors), warnings=tuple(warnings))


def _validate_command_list(
    commands: dict[str, Any],
    key: str,
    bucket: set[str],
    errors: list[str],
) -> None:
    values = commands.get(key)
    if values is None:
        return
    if not isinstance(values, list):
        errors.append(f"commands.{key} must be a list of shell patterns")
        return
    for index, value in enumerate(values):
        if not isinstance(value, str):
            errors.append(f"commands.{key}[{index}] must be a string")
            continue
        candidate = value.strip()
        if not candidate:
            errors.append(f"commands.{key}[{index}] must not be empty")
            continue
        if candidate in bucket:
            errors.append(f"commands.{key} contains duplicate entry '{candidate}'")
            continue
        bucket.add(candidate)


def _validate_regex(value: Any, validator_name: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(
            f"Validator '{validator_name}' option 'arguments_regex' must be a non-empty string"
        )
        return
    try:
        re.compile(value)
    except re.error as exc:
        errors.append(
            f"Validator '{validator_name}' option 'arguments_regex' is not a valid regex: {exc}"
        )


def _is_supported_value(value: Any) -> bool:
    if isinstance(value, _SIMPLE_VALUE_TYPES):
        return True
    if isinstance(value, list):
        return all(_is_supported_value(item) for item in value)
    if isinstance(value, dict):
        return all(isinstance(key, str) and _is_supported_value(val) for key, val in value.items())
    return False


def validate_policy_file(path: Path | str) -> PolicyValidationResult:
    """Load and validate a policy located at ``path``."""

    document = load_policy_document(path)
    return validate_policy_document(document)


__all__ = [
    "PolicyValidationError",
    "PolicyValidationResult",
    "validate_policy_document",
    "validate_policy_file",
    "load_policy_document",
]
