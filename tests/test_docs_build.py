"""Ensure the MkDocs site builds successfully."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_mkdocs_build(tmp_path: Path) -> None:
    """`mkdocs build` should succeed and render key pages."""
    repo_root = Path(__file__).resolve().parent.parent
    site_dir = tmp_path / "site"
    site_dir.mkdir()

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "mkdocs",
            "build",
            "--strict",
            "--site-dir",
            str(site_dir),
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, f"mkdocs build failed: {result.stdout}\n{result.stderr}"

    index_html = site_dir / "index.html"
    api_html = site_dir / "api" / "index.html"

    assert index_html.exists(), "mkdocs build did not produce index.html"
    assert api_html.exists(), "mkdocs build did not render the API reference"

    html_text = index_html.read_text(encoding="utf-8")
    assert "Gabriel Documentation" in html_text
