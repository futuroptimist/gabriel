"""Utilities for collecting and normalizing local knowledge sources."""

from __future__ import annotations

from .text import (
    HiddenCharacter,
    _HTMLTextExtractor,
    _character_name,
    find_hidden_characters,
    format_findings,
    iter_hidden_characters,
    main,
    normalize_allow_value,
    sanitize_prompt,
    scan_path,
    scan_paths,
)

__all__ = [
    "HiddenCharacter",
    "_HTMLTextExtractor",
    "_character_name",
    "find_hidden_characters",
    "format_findings",
    "iter_hidden_characters",
    "main",
    "normalize_allow_value",
    "sanitize_prompt",
    "scan_path",
    "scan_paths",
]
