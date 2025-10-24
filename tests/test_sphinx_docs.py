from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_sphinx_builds_successfully(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    build_dir = tmp_path / "sphinx"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/build_sphinx_docs.py",
            "--output",
            str(build_dir),
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert (
        result.returncode == 0
    ), f"Sphinx build failed: {result.stdout}\n{result.stderr}"

    index_html = build_dir / "index.html"
    assert index_html.exists(), "Sphinx build did not produce index.html"

    html = index_html.read_text(encoding="utf-8")
    assert "Gabriel API Reference" in html
