"""Validate the scheduled security workflow."""

from __future__ import annotations

from pathlib import Path

import yaml


def test_security_workflow_runs_weekly_and_scans() -> None:
    """The security workflow should schedule weekly scans with the expected tools."""

    workflow_path = Path(".github/workflows/security.yml")
    assert workflow_path.exists(), "security workflow is missing"

    workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))

    triggers = workflow.get("on") or workflow.get(True) or {}
    schedule = triggers.get("schedule", [])
    cron_expressions = {entry.get("cron") for entry in schedule if isinstance(entry, dict)}
    assert "0 6 * * 1" in cron_expressions, "weekly cron schedule should fire on Mondays"
    assert "workflow_dispatch" in triggers, "workflow should support manual dispatch"

    jobs = workflow.get("jobs", {})
    expected_jobs = {"codeql", "semgrep", "dependency-audits"}
    assert expected_jobs.issubset(jobs), "security workflow must define all scanning jobs"

    codeql_steps = jobs["codeql"].get("steps", [])
    assert any(
        isinstance(step, dict)
        and str(step.get("uses", "")).startswith("github/codeql-action/init@")
        for step in codeql_steps
    ), "CodeQL job must initialize the scanner"

    semgrep_steps = jobs["semgrep"].get("steps", [])
    assert any(
        isinstance(step, dict) and "semgrep scan" in str(step.get("run", ""))
        for step in semgrep_steps
    ), "Semgrep job must invoke semgrep scan"

    dependency_steps = jobs["dependency-audits"].get("steps", [])
    assert any(
        isinstance(step, dict) and "pip-audit" in str(step.get("run", ""))
        for step in dependency_steps
    ), "Dependency audit job must run pip-audit"
    assert any(
        isinstance(step, dict) and "npm audit" in str(step.get("run", ""))
        for step in dependency_steps
    ), "Dependency audit job must run npm audit"
