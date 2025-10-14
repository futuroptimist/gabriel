"""Compatibility shim for viewer utilities.

The canonical implementation lives in :mod:`gabriel.ui.viewer`.
"""

from __future__ import annotations

from .ui import viewer as _viewer

__all__ = [
    "DEFAULT_HOST",
    "DEFAULT_PORT",
    "ViewerServer",
    "get_viewer_directory",
    "serve_viewer",
    "start_viewer_server",
]


def _main() -> None:
    """Delegate to :mod:`gabriel.ui.viewer`'s CLI entry point."""

    _viewer._main()


if __name__ == "__main__":  # pragma: no cover - CLI entry point compatibility
    _main()


DEFAULT_HOST = _viewer.DEFAULT_HOST
DEFAULT_PORT = _viewer.DEFAULT_PORT
ViewerServer = _viewer.ViewerServer
get_viewer_directory = _viewer.get_viewer_directory
serve_viewer = _viewer.serve_viewer
start_viewer_server = _viewer.start_viewer_server
