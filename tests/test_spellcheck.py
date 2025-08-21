import subprocess
from pathlib import Path


def test_spellcheck_docs() -> None:
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        ["pyspelling", "-c", ".spellcheck.yaml"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
