from __future__ import annotations

import io
import json
from pathlib import Path

import pytest

from gabriel.ui import cli


def test_cli_network_json_output(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    services = [
        {
            "name": "Public Redis",
            "port": 6379,
            "exposure": "internet",
            "authenticated": False,
            "encrypted": False,
        },
        {
            "name": "Local Admin",
            "port": 8080,
            "exposure": "local",
            "address": "0.0.0.0",
        },
    ]
    payload_path = tmp_path / "services.json"
    payload_path.write_text(json.dumps(services), encoding="utf-8")

    cli.main(["network", "--input", str(payload_path)])

    output = json.loads(capsys.readouterr().out)
    assert any(f["indicator"] == "internet-database" for f in output)
    assert any(f["indicator"] == "unauthenticated-service" for f in output)
    assert any(f["indicator"] == "wildcard-exposure" for f in output)


def test_cli_network_table_output(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    services = [
        {
            "name": "UDP Service",
            "port": 123,
            "protocol": "udp",
            "exposure": "internet",
            "encrypted": False,
        }
    ]

    monkeypatch.setattr(cli.sys, "stdin", io.StringIO(json.dumps(services)))

    cli.main(["network", "--output-format", "table"])

    out = capsys.readouterr().out.strip()
    assert "udp-amplification" in out
    assert "UDP Service:123/udp (internet)" in out


def test_cli_network_rejects_invalid_json(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli.sys, "stdin", io.StringIO("not-json"))
    with pytest.raises(SystemExit) as excinfo:
        cli.main(["network"])
    assert "Invalid JSON" in str(excinfo.value)


def test_cli_network_requires_input(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli.sys, "stdin", io.StringIO("   "))
    with pytest.raises(SystemExit) as excinfo:
        cli.main(["network"])
    assert "Network service definitions are required" in str(excinfo.value)


def test_cli_network_requires_array(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli.sys, "stdin", io.StringIO("{}"))
    with pytest.raises(SystemExit) as excinfo:
        cli.main(["network"])
    assert "JSON array" in str(excinfo.value)


def test_cli_network_rejects_non_dict_entry(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli.sys, "stdin", io.StringIO("[1]"))
    with pytest.raises(SystemExit) as excinfo:
        cli.main(["network"])
    assert "JSON object" in str(excinfo.value)


def test_cli_network_rejects_invalid_service(monkeypatch: pytest.MonkeyPatch) -> None:
    service_payload = [{"name": "", "port": 80}]
    monkeypatch.setattr(cli.sys, "stdin", io.StringIO(json.dumps(service_payload)))
    with pytest.raises(SystemExit) as excinfo:
        cli.main(["network"])
    assert "Invalid network service" in str(excinfo.value)
