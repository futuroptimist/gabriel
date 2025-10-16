"""Tests for the Docker GitHub Actions workflow configuration."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

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
        if isinstance(step, dict)
        and step.get("uses", "").startswith("docker/build-push-action@")
    ]
    assert build_steps, "Docker workflow must invoke docker/build-push-action"  # nosec B101

    build_step = build_steps[-1]
    platforms = _normalize_platforms(build_step.get("with", {}).get("platforms"))
    expected = {"linux/amd64", "linux/arm64"}
    missing = sorted(expected.difference(platforms))
    assert not missing, f"Docker build should target multi-arch platforms, missing: {missing}"  # nosec B101
