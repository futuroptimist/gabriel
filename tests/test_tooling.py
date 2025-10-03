"""Regression tests for repository tooling configuration."""

from __future__ import annotations

from importlib import import_module
from pathlib import Path
from typing import Any


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


def test_pre_commit_configuration_checks_docstrings() -> None:
    """Ensure flake8 enforces docstring style guidance."""

    config = Path(".pre-commit-config.yaml").read_text(encoding="utf-8")
    assert "- id: flake8" in config  # nosec B101
    assert "flake8-docstrings" in config  # nosec B101


def test_flake8_configuration_enables_docstring_rules() -> None:
    """Confirm flake8 is configured to surface docstring violations."""

    config = Path(".flake8").read_text(encoding="utf-8")
    assert "extend-select = D" in config  # nosec B101
    assert "tests/*.py: D100,D101,D102,D103,D104,D107" in config  # nosec B101


def test_ci_workflow_runs_ruff() -> None:
    """Ensure the CI workflow executes ruff checks."""

    workflow = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "ruff check" in workflow  # nosec B101
