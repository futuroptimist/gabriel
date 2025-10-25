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


def test_security_workflow_schedules_weekly_scans() -> None:
    """The security workflow should run weekly and cover all required scanners."""

    workflow = load_workflow("security.yml")

    triggers = workflow.get("on") or workflow.get(True)
    assert triggers is not None, "Security workflow is missing triggers"
    assert "workflow_dispatch" in triggers

    schedule = triggers.get("schedule")
    assert schedule, "Security workflow must define a schedule trigger"
    assert schedule[0]["cron"] == "0 5 * * 1"

    jobs = workflow["jobs"]
    expected_jobs = {"codeql", "semgrep", "dependency-scan"}
    assert expected_jobs.issubset(jobs), "Missing required security jobs"

    codeql_steps = [
        step.get("uses")
        for step in jobs["codeql"]["steps"]
        if isinstance(step, dict) and "uses" in step
    ]
    assert "github/codeql-action/init@v4" in codeql_steps
