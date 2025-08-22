import sys
from pathlib import Path

from pyspelling import __main__ as pyspelling_main


def test_spellcheck_docs(monkeypatch) -> None:
    root = Path(__file__).resolve().parents[1]
    monkeypatch.chdir(root)
    monkeypatch.setattr(sys, "argv", ["pyspelling", "-c", ".spellcheck.yaml"])
    assert pyspelling_main.main() is False  # nosec B101
