"""Compatibility layer re-exporting phishing heuristics from :mod:`gabriel.analysis`."""

from __future__ import annotations

from .analysis.phishing import (
    PhishingFinding,
    _registrable_domain_for,
    _split_registrable_domain,
    analyze_text_for_phishing,
    analyze_url,
    extract_urls,
)

__all__ = [
    "PhishingFinding",
    "extract_urls",
    "analyze_url",
    "analyze_text_for_phishing",
    "_registrable_domain_for",
    "_split_registrable_domain",
]
