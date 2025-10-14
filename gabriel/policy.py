"""Compatibility wrapper for the policy validators now hosted under :mod:`gabriel.analysis`."""

from __future__ import annotations

from .analysis.policy import (
    PolicyValidationError,
    PolicyValidationResult,
    load_policy_document,
    validate_policy_document,
    validate_policy_file,
)

__all__ = [
    "PolicyValidationError",
    "PolicyValidationResult",
    "load_policy_document",
    "validate_policy_document",
    "validate_policy_file",
]
