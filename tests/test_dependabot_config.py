"""Tests for Dependabot configuration."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml


def load_dependabot_config() -> dict:
    """Load the Dependabot configuration as a dictionary."""

    config_path = Path(".github/dependabot.yml")
    contents = config_path.read_text(encoding="utf-8")
    loaded = yaml.safe_load(contents)
    if not isinstance(loaded, dict):
        pytest.fail("Dependabot config must be a mapping")
    return loaded


def test_dependabot_monitors_github_actions() -> None:
    """Dependabot should track GitHub Actions updates in addition to Python packages."""

    config = load_dependabot_config()
    updates = config.get("updates", [])
    if not isinstance(updates, list):
        pytest.fail("`updates` should be a list of ecosystems")

    github_actions_entries = [
        entry
        for entry in updates
        if isinstance(entry, dict)
        and entry.get("package-ecosystem") == "github-actions"
        and entry.get("directory") == "/"
    ]

    if not github_actions_entries:
        pytest.fail("Dependabot must monitor GitHub Actions workflows")
