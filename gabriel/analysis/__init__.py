"""Analysis layer hosting phishing heuristics, policy validators, and recommendations."""

from __future__ import annotations

from .phishing import (
    PhishingFinding,
    _registrable_domain_for,
    _split_registrable_domain,
    analyze_text_for_phishing,
    analyze_url,
    extract_urls,
)
from .policy import (
    PolicyValidationError,
    PolicyValidationResult,
    load_policy_document,
    validate_policy_document,
    validate_policy_file,
)
from .recommendations import Recommendation, RiskTolerance, generate_recommendations

__all__ = [
    "PhishingFinding",
    "extract_urls",
    "analyze_url",
    "analyze_text_for_phishing",
    "_registrable_domain_for",
    "_split_registrable_domain",
    "PolicyValidationError",
    "PolicyValidationResult",
    "load_policy_document",
    "validate_policy_document",
    "validate_policy_file",
    "Recommendation",
    "RiskTolerance",
    "generate_recommendations",
]
