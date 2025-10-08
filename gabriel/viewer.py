"""Utilities for serving the WebGL model viewer assets."""

from __future__ import annotations

import contextlib
import functools
import threading
import warnings
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Iterator

VIEWER_DIRECTORY = Path(__file__).resolve().parents[1] / "viewer"


def _ensure_viewer_directory() -> None:
    if not VIEWER_DIRECTORY.exists():
        raise FileNotFoundError(
            "The viewer assets directory was not found. Expected to exist at"
            f" {VIEWER_DIRECTORY}."
        )


@contextlib.contextmanager
def serve_viewer(
    host: str = "127.0.0.1",
    port: int | None = None,
    open_browser: bool = True,
    index: str = "index.html",
) -> Iterator[ThreadingHTTPServer]:
    """Serve the WebGL viewer assets with a lightweight HTTP server.

    Parameters
    ----------
    host:
        The interface to bind. Defaults to loopback for local-only access.
    port:
        The port to bind. When ``None`` (default) an ephemeral port is selected.
    open_browser:
        Whether to automatically open the viewer in the default browser.
    index:
        The initial path to open when ``open_browser`` is ``True``.

    Yields
    ------
    ThreadingHTTPServer
        The running HTTP server instance. Call ``shutdown`` on the server to
        terminate the serving thread.
    """

    _ensure_viewer_directory()

    if port is None:
        port = 0

    handler_factory = functools.partial(
        SimpleHTTPRequestHandler,
        directory=str(VIEWER_DIRECTORY),
    )

    with ThreadingHTTPServer((host, port), handler_factory) as server:
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            if open_browser:
                url_host = host
                if host in {"0.0.0.0", "::"}:  # nosec B104 - normalize wildcard hosts
                    url_host = "127.0.0.1"
                url = f"http://{url_host}:{server.server_port}/{index}"
                try:
                    webbrowser.open(url)
                except webbrowser.Error as exc:  # pragma: no cover - depends on system config
                    warnings.warn(
                        f"Failed to open browser automatically: {exc}",
                        stacklevel=2,
                    )
            yield server
        finally:
            server.shutdown()
            thread.join()


def main(argv: list[str] | None = None) -> None:
    """Command-line entry point for launching the viewer server."""

    import argparse

    parser = argparse.ArgumentParser(description="Serve the Gabriel WebGL viewer")
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Interface to bind. Defaults to 127.0.0.1 for local-only access.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Port to bind. Defaults to an ephemeral port.",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not open a browser window automatically.",
    )
    parser.add_argument(
        "--index",
        default="index.html",
        help="Path to open relative to the viewer directory.",
    )

    args = parser.parse_args(argv)

    with serve_viewer(
        host=args.host,
        port=args.port,
        open_browser=not args.no_browser,
        index=args.index,
    ) as server:
        address = server.server_address
        if isinstance(address, tuple):
            raw_host = address[0]
            active_port = address[1]
        else:
            raw_host = address
            active_port = server.server_port
        if isinstance(raw_host, bytes):
            bind_host = raw_host.decode("utf-8", "ignore")
        else:
            bind_host = str(raw_host)
        print("Serving viewer at " f"http://{bind_host}:{active_port}/{args.index}")
        print("Press Ctrl+C to stop.")
        try:
            threading.Event().wait()
        except KeyboardInterrupt:
            print("\nShutting down viewer server...")


__all__ = ["serve_viewer", "main", "VIEWER_DIRECTORY"]


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()
