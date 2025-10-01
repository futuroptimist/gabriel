"""Tests for the developer bootstrap script."""

from __future__ import annotations

import os
import stat
import subprocess  # nosec B404
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_setup_script_exists_and_is_executable() -> None:
    script = REPO_ROOT / "scripts" / "setup.sh"
    assert script.exists(), "scripts/setup.sh should exist to match runbook instructions"  # nosec B101
    mode = script.stat().st_mode
    assert mode & stat.S_IXUSR, "scripts/setup.sh must be executable"  # nosec B101


def test_setup_script_supports_dry_run() -> None:
    script = REPO_ROOT / "scripts" / "setup.sh"
    result = subprocess.run(
        ["bash", str(script), "--dry-run"],
        check=True,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        env={**os.environ, "CI": "1"},
    )  # nosec B603 B607
    stdout = result.stdout
    assert "-m venv" in stdout  # nosec B101
    assert "pre-commit install" in stdout  # nosec B101
