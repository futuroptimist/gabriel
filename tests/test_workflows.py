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


def test_mkdocs_pages_deploys_only_when_pages_is_enabled() -> None:
    """The Pages workflow should validate docs on PRs and only deploy configured Pages sites."""
    workflow = load_workflow("mkdocs-pages.yml")
    build_job = workflow["jobs"]["build"]
    deploy_job = workflow["jobs"]["deploy"]

    assert build_job["outputs"]["pages-enabled"] == "${{ steps.pages.outputs.enabled }}"
    assert (
        deploy_job["if"]
        == "github.event_name != 'pull_request' && needs.build.outputs.pages-enabled == 'true'"
    )

    steps = build_job["steps"]
    pages_check = next(step for step in steps if step.get("id") == "pages")
    assert pages_check["if"] == "github.event_name != 'pull_request'"
    assert 'get("build_type", "")' in pages_check["run"]  # nosec B101
    assert '[ "$build_type" = "workflow" ]' in pages_check["run"]  # nosec B101
    assert "build_type='${build_type:-unknown}', not 'workflow'" in pages_check["run"]  # nosec B101

    upload_step = next(
        step for step in steps if step.get("uses") == "actions/upload-pages-artifact@v3"
    )
    assert (
        upload_step["if"]
        == "github.event_name != 'pull_request' && steps.pages.outputs.enabled == 'true'"
    )
