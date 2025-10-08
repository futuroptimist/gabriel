from __future__ import annotations

import contextlib
import time
import urllib.request
import webbrowser
from http.server import ThreadingHTTPServer
from unittest import mock

import pytest

import gabriel.viewer as viewer
from gabriel.viewer import VIEWER_DIRECTORY, serve_viewer


def _viewer_url(server: ThreadingHTTPServer) -> str:
    raw_host, port = server.server_address
    if isinstance(raw_host, bytes | bytearray):
        decoded_host = raw_host.decode("utf-8", "ignore")
    else:
        decoded_host = str(raw_host)
    host = decoded_host or ""
    if not host or host == "0.0.0.0":  # nosec B104 - normalize wildcard host for tests
        host = "127.0.0.1"
    return f"http://{host}:{port}/index.html"


def test_serve_viewer_serves_index_page() -> None:
    with serve_viewer(open_browser=False, port=0) as server:
        url = _viewer_url(server)
        time.sleep(0.05)
        with urllib.request.urlopen(url) as response:  # nosec B310 - local HTTP fetch
            body = response.read().decode("utf-8")
    assert "model-viewer" in body  # nosec B101
    assert VIEWER_DIRECTORY.name == "viewer_assets"  # nosec B101


def test_serve_viewer_opens_browser_from_lan_host() -> None:
    with mock.patch("gabriel.viewer.webbrowser.open", return_value=True) as open_mock:
        with serve_viewer(host="0.0.0.0", open_browser=True) as server:  # nosec B104
            # Ensure the server spun up and captured by the context manager.
            assert server.server_address[1] > 0  # nosec B101
    open_mock.assert_called_once()
    url = open_mock.call_args[0][0]
    assert "127.0.0.1" in url  # nosec B101


def test_serve_viewer_warns_when_browser_launch_fails() -> None:
    error = webbrowser.Error("disabled")
    with mock.patch("gabriel.viewer.webbrowser.open", side_effect=error):
        with mock.patch("gabriel.viewer.warnings.warn") as warn_mock:
            with serve_viewer(open_browser=True) as server:
                assert server.server_address[1] > 0  # nosec B101
    warn_mock.assert_called_once()
    assert "disabled" in warn_mock.call_args[0][0]  # nosec B101


def test_ensure_viewer_directory_missing() -> None:
    fake_path = mock.Mock()
    fake_path.exists.return_value = False
    with mock.patch.object(viewer, "VIEWER_DIRECTORY", fake_path):
        with pytest.raises(FileNotFoundError):
            viewer._ensure_viewer_directory()


def test_main_handles_keyboard_interrupt(capsys: pytest.CaptureFixture[str]) -> None:
    @contextlib.contextmanager
    def fake_server(**kwargs):
        yield mock.Mock(server_address=("127.0.0.1", 9999), server_port=9999)

    class FakeEvent:
        def wait(self) -> None:
            raise KeyboardInterrupt

    with mock.patch.object(viewer, "serve_viewer", fake_server):
        with mock.patch.object(viewer.threading, "Event", return_value=FakeEvent()):
            viewer.main(["--no-browser", "--host", "127.0.0.1", "--port", "9999"])

    captured = capsys.readouterr()
    assert "Serving viewer at" in captured.out  # nosec B101
    assert "Shutting down viewer server" in captured.out  # nosec B101


def test_main_formats_non_tuple_address(capsys: pytest.CaptureFixture[str]) -> None:
    @contextlib.contextmanager
    def fake_server(**kwargs):
        yield mock.Mock(server_address="pipe", server_port=7777)

    class FakeEvent:
        def wait(self) -> None:
            raise KeyboardInterrupt

    with mock.patch.object(viewer, "serve_viewer", fake_server):
        with mock.patch.object(viewer.threading, "Event", return_value=FakeEvent()):
            viewer.main(
                ["--no-browser", "--host", "127.0.0.1", "--port", "7777", "--index", "viewer.html"]
            )

    captured = capsys.readouterr()
    assert "http://pipe:7777/viewer.html" in captured.out  # nosec B101


def test_main_formats_byte_address(capsys: pytest.CaptureFixture[str]) -> None:
    @contextlib.contextmanager
    def fake_server(**kwargs):
        yield mock.Mock(server_address=b"pipe", server_port=4242)

    class FakeEvent:
        def wait(self) -> None:
            raise KeyboardInterrupt

    with mock.patch.object(viewer, "serve_viewer", fake_server):
        with mock.patch.object(viewer.threading, "Event", return_value=FakeEvent()):
            viewer.main(["--no-browser", "--host", "127.0.0.1", "--port", "4242"])

    captured = capsys.readouterr()
    assert "http://pipe:4242/index.html" in captured.out  # nosec B101
