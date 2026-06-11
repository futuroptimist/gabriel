"""Tests for the Docker GitHub Actions workflow configuration."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

import pytest
import yaml


@pytest.fixture(scope="module")
def docker_workflow_path() -> Path:
    """Return the path to the Docker workflow file."""

    path = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "docker.yml"
    if not path.exists():
        pytest.fail("Docker workflow file is missing from repository")
    return path


def _normalize_platforms(raw: object) -> set[str]:
    """Normalize the platforms declaration into a comparable set."""

    if isinstance(raw, str):
        items: Iterable[str] = (part.strip() for part in raw.split(","))
    elif isinstance(raw, Iterable):
        items = (str(part).strip() for part in raw)
    else:  # pragma: no cover - defensive guard for unexpected schema changes
        return set()
    return {item for item in items if item}


def test_docker_workflow_targets_multi_architectures(docker_workflow_path: Path) -> None:
    """Ensure the Docker build publishes manifests for amd64 and arm64."""

    workflow = yaml.safe_load(docker_workflow_path.read_text(encoding="utf-8"))
    build_job = workflow.get("jobs", {}).get("build")
    assert build_job is not None, "Docker workflow must define a build job"  # nosec B101

    steps = build_job.get("steps", [])
    build_steps = [
        step
        for step in steps
        if isinstance(step, dict) and step.get("uses", "").startswith("docker/build-push-action@")
    ]
    assert build_steps, "Docker workflow must invoke docker/build-push-action"  # nosec B101

    build_step = build_steps[-1]
    platforms = _normalize_platforms(build_step.get("with", {}).get("platforms"))
    expected = {"linux/amd64", "linux/arm64"}
    missing = sorted(expected.difference(platforms))
    assert (
        not missing
    ), f"Docker build should target multi-arch platforms, missing: {missing}"  # nosec B101


def test_trivy_action_uses_existing_version_tag(docker_workflow_path: Path) -> None:
    """Guard against typoing the Trivy action ref and failing workflow setup."""

    workflow = yaml.safe_load(docker_workflow_path.read_text(encoding="utf-8"))
    scan_job = workflow.get("jobs", {}).get("scan")
    assert scan_job is not None, "Docker workflow must define a scan job"  # nosec B101

    trivy_steps = [
        step
        for step in scan_job.get("steps", [])
        if isinstance(step, dict)
        and str(step.get("uses", "")).startswith("aquasecurity/trivy-action@")
    ]
    assert trivy_steps, "Docker workflow must scan images with Trivy"  # nosec B101

    expected_ref = "aquasecurity/trivy-action@v0.36.0"
    unexpected_refs = sorted(
        {str(step["uses"]) for step in trivy_steps if step.get("uses") != expected_ref}
    )
    assert (
        not unexpected_refs
    ), f"Every Trivy scan step should use {expected_ref}, found: {unexpected_refs}"  # nosec B101


def test_trivy_action_uses_supported_vulnerability_type_input(
    docker_workflow_path: Path,
) -> None:
    """Ensure Trivy scans both OS and library packages with supported action inputs."""

    workflow = yaml.safe_load(docker_workflow_path.read_text(encoding="utf-8"))
    scan_job = workflow.get("jobs", {}).get("scan")
    assert scan_job is not None, "Docker workflow must define a scan job"  # nosec B101

    trivy_steps = [
        step
        for step in scan_job.get("steps", [])
        if isinstance(step, dict)
        and str(step.get("uses", "")).startswith("aquasecurity/trivy-action@")
    ]
    assert trivy_steps, "Docker workflow must scan images with Trivy"  # nosec B101

    for step in trivy_steps:
        config = step.get("with", {})
        assert config.get("vuln-type") == "os,library"  # nosec B101
        assert "pkg-types" not in config  # nosec B101


def test_docker_workflow_does_not_push_on_pull_requests(docker_workflow_path: Path) -> None:
    """Ensure pull requests validate the image build without publishing to GHCR."""

    workflow = yaml.safe_load(docker_workflow_path.read_text(encoding="utf-8"))
    build_job = workflow.get("jobs", {}).get("build")
    assert build_job is not None, "Docker workflow must define a build job"  # nosec B101

    steps = build_job.get("steps", [])
    login_steps = [
        step
        for step in steps
        if isinstance(step, dict) and step.get("uses", "").startswith("docker/login-action@")
    ]
    assert login_steps, "Docker workflow must log in before publishing"  # nosec B101
    assert login_steps[-1].get("if") == "github.event_name != 'pull_request'"  # nosec B101

    build_steps = [
        step
        for step in steps
        if isinstance(step, dict) and step.get("uses", "").startswith("docker/build-push-action@")
    ]
    assert build_steps, "Docker workflow must invoke docker/build-push-action"  # nosec B101
    assert (
        build_steps[-1].get("with", {}).get("push") == "${{ github.event_name != 'pull_request' }}"
    )  # nosec B101
