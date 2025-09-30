import shutil
import sys
from pathlib import Path

import pytest
from pyspelling import __main__ as pyspelling_main


def test_spellcheck_docs(monkeypatch) -> None:
    if shutil.which("aspell") is None:
        pytest.skip("aspell binary is required for spellcheck tests")
    root = Path(__file__).resolve().parents[1]
    monkeypatch.chdir(root)
    monkeypatch.setattr(sys, "argv", ["pyspelling", "-c", ".spellcheck.yaml"])
    assert pyspelling_main.main() is False  # nosec B101
