"""Regression tests for repository tooling configuration."""

from __future__ import annotations

import json
from importlib import import_module
from pathlib import Path
from typing import Any

import pytest


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


def test_pytest_addopts_enforces_coverage_threshold() -> None:
    """Ensure pytest defaults fail when coverage drops below the target."""

    config = Path("pyproject.toml").read_text(encoding="utf-8")
    data = toml_loader.loads(config)

    addopts = data["tool"]["pytest"]["ini_options"]["addopts"]
    assert "--cov-fail-under=100" in addopts  # nosec B101


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
