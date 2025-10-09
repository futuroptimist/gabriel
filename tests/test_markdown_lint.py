"""Ensure Markdown files comply with the PyMarkdown ruleset."""

from __future__ import annotations

import shutil
import subprocess  # nosec B404
from pathlib import Path

import pytest


def test_pymarkdown_scan() -> None:
    if shutil.which("pymarkdown") is None:
        pytest.skip("pymarkdown binary is required for markdown lint tests")
    repo_root = Path(__file__).resolve().parents[1]
    config = repo_root / ".pymarkdown.json"
    cmd = [
        "pymarkdown",
        "--config",
        str(config),
        "scan",
        "-r",
        str(repo_root),
    ]
    result = subprocess.run(  # nosec B603
        cmd, capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        raise AssertionError(result.stdout + result.stderr)
