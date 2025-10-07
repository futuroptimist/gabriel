"""Tests for the repository's Markdown lint configuration."""

from __future__ import annotations

import json
from pathlib import Path


def test_markdown_line_length_budget() -> None:
    """Ensure the Markdown lint configuration enforces the repo's 100 char limit."""
    config_path = Path(__file__).resolve().parents[1] / ".pymarkdown.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    md013 = config["plugins"]["md013"]
    assert md013["line_length"] == 100  # nosec: unit tests rely on assertions
    assert md013["heading_line_length"] == 100  # nosec: unit tests rely on assertions
    assert (
        md013["code_block_line_length"] >= 100
    )  # nosec: documenting rationale for wide code blocks
