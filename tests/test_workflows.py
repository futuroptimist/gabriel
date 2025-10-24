"""Tests for GitHub Actions workflow configuration."""

from __future__ import annotations

from pathlib import Path

import yaml


def load_workflow(name: str) -> dict:
    """Load a workflow file from the .github/workflows directory."""
    workflow_path = Path(".github/workflows") / name
    return yaml.safe_load(workflow_path.read_text())


def test_coverage_workflow_runs_on_multiple_operating_systems() -> None:
    """The coverage workflow should exercise Linux, macOS, and Windows runners."""
    workflow = load_workflow("coverage.yml")
    coverage_job = workflow["jobs"]["coverage"]

    assert coverage_job["runs-on"] == "${{ matrix.os }}"

    matrix = coverage_job["strategy"]["matrix"]
    assert matrix["os"] == [
        "ubuntu-latest",
        "macos-latest",
        "windows-latest",
    ]
    assert matrix["python-version"] == ["3.10", "3.11"]
