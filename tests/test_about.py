"""Tests covering package metadata for Gabriel."""

from __future__ import annotations

import importlib
import importlib.util
from pathlib import Path
from types import ModuleType
from typing import TypedDict, cast


class ProjectLicense(TypedDict):
    """Typed representation of the ``project.license`` table."""

    file: str


class ProjectAuthor(TypedDict):
    """Typed representation of each entry in ``project.authors``."""

    name: str


class ProjectUrls(TypedDict):
    """Typed representation of the ``project.urls`` table used in tests."""

    Homepage: str
    Documentation: str
    Source: str
    Issues: str


class ProjectMetadata(TypedDict):
    """Subset of pyproject metadata required for the tests."""

    name: str
    version: str
    description: str
    readme: str
    license: ProjectLicense
    authors: list[ProjectAuthor]
    keywords: list[str]
    classifiers: list[str]
    urls: ProjectUrls


def _load_toml_module() -> ModuleType:
    module_name = "tomllib"
    if importlib.util.find_spec(module_name) is None:
        module_name = "tomli"
    return importlib.import_module(module_name)


def _load_project_table() -> ProjectMetadata:
    toml_module = _load_toml_module()
    with Path("pyproject.toml").open("rb") as handle:
        pyproject = toml_module.load(handle)
    return cast(ProjectMetadata, pyproject["project"])


def test_pyproject_contains_required_metadata() -> None:
    project = _load_project_table()

    assert project["description"].strip()  # nosec B101 - pytest assertion
    assert project["readme"] == "README.md"  # nosec B101 - pytest assertion
    assert project["license"]["file"] == "LICENSE"  # nosec B101 - pytest assertion
    assert project["authors"], "authors list should not be empty"  # nosec B101 - pytest assertion
    assert project["keywords"], "keywords list should not be empty"  # nosec B101 - pytest assertion
    assert project["classifiers"], "classifiers list should not be empty"  # nosec B101 - pytest assertion
    urls = project.get("urls", {})
    assert "Homepage" in urls  # nosec B101 - pytest assertion
    assert "Source" in urls  # nosec B101 - pytest assertion


def test_about_metadata_matches_pyproject() -> None:
    project = _load_project_table()
    about = importlib.import_module("gabriel.__about__")

    assert about.__title__ == project["name"]  # nosec B101 - pytest assertion
    assert about.__version__ == project["version"]  # nosec B101 - pytest assertion
    assert about.__summary__ == project["description"]  # nosec B101 - pytest assertion
    urls = project["urls"]
    assert about.__uri__ == urls["Homepage"]  # nosec B101 - pytest assertion
    author_names = [author["name"] for author in project["authors"]]
    assert about.__author__ in author_names  # nosec B101 - pytest assertion
    assert tuple(project["keywords"]) == about.__keywords__  # nosec B101 - pytest assertion
    assert about.__license__ == "MIT"  # nosec B101 - pytest assertion
