"""Regression tests for repository tooling configuration."""

from __future__ import annotations

import tomllib
from pathlib import Path


def test_lychee_configuration_exists_and_excludes_prompts() -> None:
    """Ensure the markdown link checker configuration is present and scoped appropriately."""

    config_path = Path("lychee.toml")
    assert config_path.exists(), "Expected lychee.toml to exist"  # nosec B101

    content = config_path.read_text(encoding="utf-8")
    data = tomllib.loads(content)

    assert data.get("no_progress") is True  # nosec B101
    assert "^docs/prompts/" in data.get("exclude_path", []), "docs prompts should be excluded"  # nosec B101
    assert "^mailto:" in data.get("exclude", []), "mailto links should remain ignored"  # nosec B101
