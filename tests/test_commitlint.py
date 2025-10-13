"""Tests covering the commitlint configuration."""

from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def package_json() -> dict[str, object]:
    path = Path("package.json")
    if not path.exists():  # pragma: no cover - defensive guard for clearer failure
        pytest.fail("package.json missing; commitlint dependencies are not installed")
    return json.loads(path.read_text(encoding="utf-8"))


def test_commitlint_config_extends_conventional() -> None:
    config_path = Path("commitlint.config.cjs")
    assert config_path.exists(), "commitlint configuration file is missing"
    contents = config_path.read_text(encoding="utf-8")
    assert "@commitlint/config-conventional" in contents


def test_commitlint_dependencies_present(package_json: dict[str, object]) -> None:
    dev_deps = package_json.get("devDependencies")
    assert isinstance(dev_deps, dict), "devDependencies not defined"
    assert "@commitlint/cli" in dev_deps
    assert "@commitlint/config-conventional" in dev_deps


def test_commitlint_script_documented(package_json: dict[str, object]) -> None:
    scripts = package_json.get("scripts")
    assert isinstance(scripts, dict), "npm scripts missing"
    assert "commitlint" in scripts, "commitlint npm script missing"
