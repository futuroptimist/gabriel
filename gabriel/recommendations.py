"""Compatibility wrapper exposing recommendation helpers from :mod:`gabriel.analysis`."""

from __future__ import annotations

from .analysis.recommendations import (
    Recommendation,
    RiskTolerance,
    generate_recommendations,
)

__all__ = [
    "Recommendation",
    "RiskTolerance",
    "generate_recommendations",
]
