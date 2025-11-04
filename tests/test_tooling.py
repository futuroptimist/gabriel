"""Regression tests for repository tooling configuration."""

from __future__ import annotations

import json
from importlib import import_module
from pathlib import Path
from typing import Any

import pytest
import yaml


def _load_toml_module() -> Any:
    try:
        return import_module("tomllib")
    except ModuleNotFoundError:  # pragma: no cover - only triggered on Python 3.10
        return import_module("tomli")


toml_loader = _load_toml_module()


def test_lychee_configuration_exists_and_excludes_prompts() -> None:
    """Ensure the markdown link checker configuration is present and scoped appropriately."""

    config_path = Path("lychee.toml")
    assert config_path.exists(), "Expected lychee.toml to exist"  # nosec B101

    content = config_path.read_text(encoding="utf-8")
    data = toml_loader.loads(content)

    assert data.get("no_progress") is True  # nosec B101
    assert "^docs/prompts/" in data.get(
        "exclude_path", []
    ), "docs prompts should be excluded"  # nosec B101
    assert "^mailto:" in data.get("exclude", []), "mailto links should remain ignored"  # nosec B101


def test_pre_commit_configuration_runs_ruff() -> None:
    """Verify ruff linting is enforced via pre-commit."""

    config = Path(".pre-commit-config.yaml").read_text(encoding="utf-8")
    assert "https://github.com/astral-sh/ruff-pre-commit" in config  # nosec B101
    assert "- id: ruff" in config  # nosec B101


def test_pytest_addopts_includes_coverage() -> None:
    """Ensure pytest is configured to run coverage analysis."""

    config = Path("pyproject.toml").read_text(encoding="utf-8")
    data = toml_loader.loads(config)

    addopts = data["tool"]["pytest"]["ini_options"]["addopts"]
    assert "--cov=gabriel" in addopts  # nosec B101


def test_pre_commit_configuration_checks_docstrings() -> None:
    """Ensure flake8 enforces docstring style guidance."""

    config = Path(".pre-commit-config.yaml").read_text(encoding="utf-8")
    assert "- id: flake8" in config  # nosec B101
    assert "flake8-docstrings" in config  # nosec B101


def test_pre_commit_configuration_runs_pydocstyle() -> None:
    """Ensure pydocstyle enforces docstring presence on package modules."""

    config = Path(".pre-commit-config.yaml").read_text(encoding="utf-8")
    assert "https://github.com/PyCQA/pydocstyle" in config  # nosec B101
    assert "pydocstyle (gabriel package)" in config  # nosec B101


def test_pre_commit_configuration_runs_eslint_for_viewer() -> None:
    """Ensure viewer JavaScript is linted via pre-commit."""

    config = Path(".pre-commit-config.yaml").read_text(encoding="utf-8")
    assert "https://github.com/pre-commit/mirrors-eslint" in config  # nosec B101
    assert "ESLint viewer JavaScript" in config  # nosec B101
    assert "viewer/(?!model-viewer" in config  # nosec B101


def test_pre_commit_configuration_runs_prettier_for_viewer() -> None:
    """Ensure viewer assets are formatted consistently via Prettier."""

    config = Path(".pre-commit-config.yaml").read_text(encoding="utf-8")
    assert "https://github.com/pre-commit/mirrors-prettier" in config  # nosec B101
    assert "Prettier viewer assets" in config  # nosec B101


def test_pre_commit_configuration_runs_semgrep() -> None:
    """Verify Semgrep static analysis runs via pre-commit."""

    config = Path(".pre-commit-config.yaml").read_text(encoding="utf-8")
    assert "https://github.com/returntocorp/semgrep" in config  # nosec B101
    assert "config/semgrep/rules.yaml" in config  # nosec B101


def test_commitlint_configured_across_tooling() -> None:
    """Ensure commitlint enforces Conventional Commits locally and in CI."""

    config = Path(".pre-commit-config.yaml").read_text(encoding="utf-8")
    assert "commitlint --edit" in config  # nosec B101
    assert "stages: [commit-msg]" in config  # nosec B101

    config_path = Path("commitlint.config.cjs")
    assert config_path.exists(), "Expected commitlint.config.cjs to exist"  # nosec B101

    package = json.loads(Path("package.json").read_text(encoding="utf-8"))
    assert package["scripts"]["lint:commits"] == "python scripts/run_commitlint.py"  # nosec B101
    assert "@commitlint/cli" in package["devDependencies"]  # nosec B101
    assert "@commitlint/config-conventional" in package["devDependencies"]  # nosec B101

    workflow = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "npm run lint:commits" in workflow  # nosec B101


def test_eslint_configuration_targets_browser_scripts() -> None:
    """Verify the ESLint configuration supports modern browser code."""

    config_path = Path(".eslintrc.json")
    assert config_path.exists(), "Expected .eslintrc.json to exist"  # nosec B101

    config = json.loads(config_path.read_text(encoding="utf-8"))
    assert config["env"]["browser"] is True  # nosec B101
    assert "eslint:recommended" in config["extends"]  # nosec B101


def test_flake8_configuration_enables_docstring_rules() -> None:
    """Confirm flake8 is configured to surface docstring violations."""

    config = Path(".flake8").read_text(encoding="utf-8")
    assert "extend-select = D" in config  # nosec B101
    assert "tests/*.py: D100,D101,D102,D103,D104,D107" in config  # nosec B101


def test_ci_workflow_runs_ruff() -> None:
    """Ensure the CI workflow executes ruff checks."""

    workflow = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "ruff check" in workflow  # nosec B101


def test_ci_workflow_runs_pre_commit() -> None:
    """Ensure CI executes the pre-commit hooks for parity with local runs."""

    workflow = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "pre-commit run --all-files" in workflow  # nosec B101


def test_docker_workflow_scans_image_for_vulnerabilities() -> None:
    """Validate that Docker publishes run a Trivy scan before pushing images."""

    workflow = yaml.safe_load(Path(".github/workflows/docker.yml").read_text(encoding="utf-8"))

    scan_job = workflow["jobs"].get("scan")
    assert scan_job is not None, "Expected scan job to guard Docker publishes"  # nosec B101

    matrix = scan_job.get("strategy", {}).get("matrix", {})
    platforms = matrix.get("platform", [])
    assert set(platforms) == {"linux/amd64", "linux/arm64"}  # nosec B101

    scan_steps = scan_job["steps"]

    # Check that platform tag step exists to sanitize the tag
    platform_tag_step = next(
        (step for step in scan_steps if step.get("name") == "Set platform tag"),
        None,
    )
    assert (
        platform_tag_step is not None
    ), "Expected platform-tag step to sanitize Docker tag"  # nosec B101

    build_step = next(
        (step for step in scan_steps if step.get("uses") == "docker/build-push-action@v6"),
        None,
    )
    assert (
        build_step is not None
    ), "Expected build step to create an image per architecture"  # nosec B101

    build_config = build_step.get("with", {})
    assert build_config.get("platforms") == "${{ matrix.platform }}"  # nosec B101
    assert build_config.get("load") is True  # nosec B101
    assert build_config.get("tags") == (
        "ghcr.io/${{ github.repository }}:scan-${{ steps.platform-tag.outputs.tag }}"
    )  # nosec B101

    trivy_step = next(
        (
            step
            for step in scan_steps
            if str(step.get("uses", "")).startswith("aquasecurity/trivy-action@")
        ),
        None,
    )
    assert trivy_step is not None, "Trivy scan step missing from Docker workflow"  # nosec B101

    trivy_config = trivy_step.get("with", {})
    assert (
        trivy_config.get("image-ref")
        == "ghcr.io/${{ github.repository }}:scan-${{ steps.platform-tag.outputs.tag }}"
    )  # nosec B101
    assert trivy_config.get("severity") == "CRITICAL,HIGH"  # nosec B101
    assert trivy_config.get("exit-code") == "1"  # nosec B101

    build_job = workflow["jobs"].get("build")
    assert build_job is not None, "Expected build job to push the release images"  # nosec B101
    assert build_job.get("needs") == "scan"  # nosec B101


def test_workflows_cover_supported_python_versions() -> None:
    """Ensure CI pipelines exercise every supported Python runtime."""

    from gabriel import SUPPORTED_PYTHON_VERSIONS

    workflow_ci = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")
    workflow_coverage = Path(".github/workflows/coverage.yml").read_text(encoding="utf-8")

    for version in SUPPORTED_PYTHON_VERSIONS:
        assert version in workflow_ci, f"CI workflow missing Python {version}"  # nosec B101
        assert (
            version in workflow_coverage
        ), f"Coverage workflow missing Python {version}"  # nosec B101


def test_release_drafter_configuration_and_workflow_exist() -> None:
    """Validate Release Drafter config and workflow are present and wired together."""

    config_path = Path(".github/release-drafter.yml")
    assert config_path.exists(), "Expected .github/release-drafter.yml to exist"  # nosec B101

    config = config_path.read_text(encoding="utf-8")
    for marker in (
        "name-template:",
        "categories:",
        "autolabeler:",
        "exclude-labels:",
    ):
        assert marker in config, f"Release Drafter config missing {marker}"  # nosec B101

    workflow_path = Path(".github/workflows/release-drafter.yml")
    assert workflow_path.exists(), "Expected Release Drafter workflow to exist"  # nosec B101

    workflow = workflow_path.read_text(encoding="utf-8")
    assert "release-drafter/release-drafter@" in workflow  # nosec B101
    assert "config-name: release-drafter.yml" in workflow  # nosec B101
    assert "branches:\n      - main" in workflow  # nosec B101


def test_cli_viewer_invokes_helper(monkeypatch: pytest.MonkeyPatch) -> None:
    from gabriel import utils as utils_module

    recorded: dict[str, Any] = {}

    def fake_serve(host: str, port: int, open_browser: bool) -> None:
        recorded["args"] = (host, port, open_browser)

    monkeypatch.setattr(utils_module, "serve_viewer", fake_serve)
    monkeypatch.setattr("gabriel.ui.cli.serve_viewer", fake_serve)

    utils_module.main(
        ["viewer", "--host", "0.0.0.0", "--port", "9999", "--no-browser"]  # nosec B104
    )

    assert recorded["args"] == ("0.0.0.0", 9999, False)  # nosec B101 B104
