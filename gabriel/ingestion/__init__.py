"""Evidence collection helpers for the Gabriel ingestion module."""

from __future__ import annotations

from .knowledge import KnowledgeStore, Note, SearchResult, load_notes_from_paths
from .text import (
    HiddenCharacter,
    find_hidden_characters,
    format_findings,
    sanitize_prompt,
    scan_path,
    scan_paths,
)

__all__ = [
    "KnowledgeStore",
    "Note",
    "SearchResult",
    "load_notes_from_paths",
    "HiddenCharacter",
    "find_hidden_characters",
    "format_findings",
    "sanitize_prompt",
    "scan_path",
    "scan_paths",
]
