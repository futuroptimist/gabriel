"""Tests for the repository's Docker ignore configuration."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def dockerignore_path() -> Path:
    """Return the path to the repository's ``.dockerignore`` file."""

    path = Path(__file__).resolve().parents[1] / ".dockerignore"
    if not path.exists():
        pytest.fail(".dockerignore file is missing from repository root")
    return path


def test_dockerignore_contains_core_exclusions(dockerignore_path: Path) -> None:
    """Ensure critical directories are excluded from the Docker build context."""

    content = dockerignore_path.read_text(encoding="utf-8").splitlines()
    expected_entries = {
        ".git",
        "__pycache__/",
        ".venv/",
        "/docs/",
        "/tests/",
    }
    missing = sorted(entry for entry in expected_entries if entry not in content)
    assert not missing, f"Missing expected .dockerignore entries: {missing}"  # nosec B101


def test_dockerignore_avoids_editor_artifacts(dockerignore_path: Path) -> None:
    """Verify that local editor settings are excluded from Docker builds."""

    content = dockerignore_path.read_text(encoding="utf-8")
    assert ".vscode/" in content  # nosec B101
    assert ".idea/" in content  # nosec B101
