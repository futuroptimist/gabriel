import sys
import threading
import time
from urllib.request import urlopen

import pytest

from gabriel.ui.viewer import (
    DEFAULT_HOST,
    get_viewer_directory,
    serve_viewer,
    start_viewer_server,
)


def test_get_viewer_directory_contains_assets() -> None:
    directory = get_viewer_directory()
    assert directory.name == "viewer"  # nosec B101
    assert (directory / "index.html").exists()  # nosec B101
    assert (directory / "viewer.js").exists()  # nosec B101


def test_start_viewer_server_serves_index() -> None:
    server_ref = None
    with start_viewer_server(port=0) as server:
        server_ref = server
        with urlopen(server.url()) as response:  # nosec B310
            payload = response.read().decode("utf-8")
    assert "Flywheel Assembly" in payload  # nosec B101
    assert server_ref is not None  # nosec B101
    server_ref.stop()


def test_serve_viewer_shutdown_event(monkeypatch: pytest.MonkeyPatch) -> None:
    opened_urls: list[str] = []

    def fake_open(url: str) -> None:
        opened_urls.append(url)

    monkeypatch.setattr("webbrowser.open", fake_open)
    ready = threading.Event()
    shutdown = threading.Event()
    thread = threading.Thread(
        target=serve_viewer,
        kwargs={
            "host": "127.0.0.1",
            "port": 0,
            "open_browser": True,
            "ready_event": ready,
            "shutdown_event": shutdown,
        },
        daemon=True,
    )
    thread.start()
    ready.wait(timeout=5)
    time.sleep(0.1)
    shutdown.set()
    thread.join(timeout=5)
    assert opened_urls  # ensure the browser helper was invoked  # nosec B101


def test_serve_viewer_handles_keyboard_interrupt(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("webbrowser.open", lambda url: None)

    call_count = {"sleep": 0}

    def fake_sleep(_: float) -> None:
        call_count["sleep"] += 1
        raise KeyboardInterrupt

    monkeypatch.setattr("gabriel.ui.viewer.time.sleep", fake_sleep)

    serve_viewer(host="127.0.0.1", port=0, open_browser=False)

    assert call_count["sleep"] == 1  # nosec B101


def test_viewer_main_invokes_serve(monkeypatch: pytest.MonkeyPatch) -> None:
    import gabriel.ui.viewer as viewer_module

    recorded: dict[str, tuple[str, int, bool]] = {}

    def fake_serve(*, host: str, port: int, open_browser: bool) -> None:
        recorded["args"] = (host, port, open_browser)

    monkeypatch.setattr(viewer_module, "serve_viewer", fake_serve)
    monkeypatch.setattr(
        sys,
        "argv",
        ["gabriel.ui.viewer", "--host", "0.0.0.0", "--port", "4321", "--no-browser"],  # nosec B104
    )

    viewer_module._main()

    assert recorded["args"] == ("0.0.0.0", 4321, False)  # nosec B101 B104


def test_legacy_viewer_shim_exports_new_helpers() -> None:
    import gabriel.viewer as legacy

    assert legacy.DEFAULT_HOST is DEFAULT_HOST  # nosec B101
    assert legacy.serve_viewer is serve_viewer  # nosec B101
    assert legacy.start_viewer_server is start_viewer_server  # nosec B101


def test_legacy_viewer_main_delegates(monkeypatch: pytest.MonkeyPatch) -> None:
    import gabriel.viewer as legacy

    called: dict[str, bool] = {"invoked": False}

    def fake_main(*args: object, **kwargs: object) -> None:
        called["invoked"] = True

    monkeypatch.setattr("gabriel.ui.viewer._main", fake_main)
    monkeypatch.setattr(
        sys,
        "argv",
        ["gabriel.viewer", "--port", "6789"],
    )

    legacy._main()

    assert called["invoked"]  # nosec B101
