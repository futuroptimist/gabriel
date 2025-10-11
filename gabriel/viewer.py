"""Utilities for serving the bundled WebGL viewer."""

from __future__ import annotations

import argparse
import contextlib
import functools
import http.server
import threading
import time
import webbrowser
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000

__all__ = [
    "DEFAULT_HOST",
    "DEFAULT_PORT",
    "ViewerServer",
    "get_viewer_directory",
    "serve_viewer",
    "start_viewer_server",
]


def get_viewer_directory() -> Path:
    """Return the directory containing the static viewer assets."""
    return Path(__file__).resolve().parents[1] / "viewer"


@dataclass
class ViewerServer:
    """Simple wrapper around the HTTP server powering the viewer."""

    host: str
    port: int
    _httpd: http.server.ThreadingHTTPServer = field(repr=False)
    _thread: threading.Thread = field(repr=False)
    _stopped: bool = field(default=False, init=False, repr=False)

    def url(self, path: str = "/") -> str:
        """Return an absolute URL pointing at the hosted viewer."""
        normalized = path.lstrip("/")
        suffix = f"/{normalized}" if normalized else "/"
        return f"http://{self.host}:{self.port}{suffix}"

    def stop(self) -> None:
        """Shut down the underlying HTTP server if it is still running."""
        if self._stopped:
            return
        self._stopped = True
        self._httpd.shutdown()
        self._thread.join()
        self._httpd.server_close()


@contextlib.contextmanager
def start_viewer_server(host: str = DEFAULT_HOST, port: int = 0) -> Iterator[ViewerServer]:
    """Start a threaded HTTP server that serves the viewer assets."""
    directory = str(get_viewer_directory())
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=directory)

    class _ThreadingViewerServer(http.server.ThreadingHTTPServer):
        daemon_threads = True
        allow_reuse_address = True

    httpd = _ThreadingViewerServer((host, port), handler)
    thread = threading.Thread(target=httpd.serve_forever, name="gabriel-viewer", daemon=True)
    thread.start()
    server = ViewerServer(host=host, port=httpd.server_address[1], _httpd=httpd, _thread=thread)
    try:
        yield server
    finally:
        server.stop()


def serve_viewer(
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    *,
    open_browser: bool = True,
    ready_event: threading.Event | None = None,
    shutdown_event: threading.Event | None = None,
) -> None:
    """Serve the WebGL viewer until interrupted."""
    with start_viewer_server(host=host, port=port) as server:
        url = server.url()
        if ready_event is not None:
            ready_event.set()
        if open_browser:
            webbrowser.open(url)
        print(f"Serving Gabriel viewer at {url}")
        if shutdown_event is None:
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("Viewer server stopped.")
        else:
            shutdown_event.wait()


def _main() -> None:
    """Entry point for ``python -m gabriel.viewer``."""
    parser = argparse.ArgumentParser(description="Serve the Gabriel WebGL viewer")
    parser.add_argument(
        "--host",
        default=DEFAULT_HOST,
        help=f"Host interface to bind (default: {DEFAULT_HOST})",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"Port to bind the server (default: {DEFAULT_PORT})",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not open the system browser automatically",
    )

    args = parser.parse_args()

    serve_viewer(host=args.host, port=args.port, open_browser=not args.no_browser)


if __name__ == "__main__":  # pragma: no cover - module level execution guard
    _main()
