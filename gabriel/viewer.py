"""Compatibility shim for ``gabriel.ui.viewer``."""

from gabriel.ui.viewer import *  # noqa: F401,F403

__all__ = [name for name in globals() if not name.startswith("_")]


if __name__ == "__main__":  # pragma: no cover - legacy CLI shim
    from gabriel.ui.viewer import _main as _viewer_main

    raise SystemExit(_viewer_main())
