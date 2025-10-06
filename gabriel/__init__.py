"""Core utilities for the Gabriel project."""

from __future__ import annotations

from .arithmetic import add, divide, floordiv, modulo, multiply, power, sqrt, subtract
from .notes import NoteDocument, NoteIndex, NoteMatch, index_security_notes
from .phishing import (
    PhishingFinding,
    analyze_text_for_phishing,
    analyze_url,
    extract_urls,
)
from .secrets import delete_secret, get_secret, store_secret

SUPPORTED_PYTHON_VERSIONS = ("3.10", "3.11")

__all__ = [
    "add",
    "subtract",
    "multiply",
    "divide",
    "power",
    "modulo",
    "floordiv",
    "sqrt",
    "store_secret",
    "get_secret",
    "delete_secret",
    "extract_urls",
    "analyze_url",
    "analyze_text_for_phishing",
    "PhishingFinding",
    "NoteDocument",
    "NoteIndex",
    "NoteMatch",
    "index_security_notes",
    "SUPPORTED_PYTHON_VERSIONS",
]
