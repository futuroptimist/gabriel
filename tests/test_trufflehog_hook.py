"""Ensure the trufflehog secret scanner stays wired into pre-commit."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml


def _load_pre_commit_config() -> dict:
    config_path = Path(__file__).resolve().parent.parent / ".pre-commit-config.yaml"
    with config_path.open(encoding="utf-8") as config_file:
        return yaml.safe_load(config_file)


def test_trufflehog_hook_enabled() -> None:
    """The trufflehog hook should be present so CI scans for leaked secrets."""

    config = _load_pre_commit_config()
    repos = config.get("repos", [])

    for repo in repos:
        if repo.get("repo") == "local":
            hooks = repo.get("hooks", [])
            for hook in hooks:
                if hook.get("id") == "trufflehog-scan":
                    assert hook.get("language") == "python"
                    assert "--max_depth" in hook.get("args", [])
                    return
            pytest.fail("Local hooks missing trufflehog-scan entry")

    pytest.fail("Local hook repository missing from pre-commit configuration")
