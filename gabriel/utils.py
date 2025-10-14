"""Compatibility shim for ``gabriel.ui`` helpers."""

from gabriel.ui.cli import *  # noqa: F401,F403
from gabriel.ui.viewer import serve_viewer as serve_viewer

__all__ = [name for name in globals() if not name.startswith("_")]


if __name__ == "__main__":  # pragma: no cover - legacy CLI shim
    from gabriel.ui.cli import main as _main

    _main()
