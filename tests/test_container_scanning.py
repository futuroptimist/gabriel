from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from types import SimpleNamespace

import pytest

from gabriel.security import (
    DEFAULT_SEVERITIES,
    TrivyError,
    TrivyNotInstalledError,
    container_scanning,
    scan_image_with_trivy,
)


def test_scan_image_builds_expected_command(monkeypatch: pytest.MonkeyPatch) -> None:
    commands: dict[str, list[str]] = {}

    def fake_which(binary: str) -> str:
        assert binary == "trivy"
        return "/usr/bin/trivy"

    def fake_run(command: Sequence[str], *args: object, **kwargs: object) -> SimpleNamespace:
        commands["command"] = list(command)
        assert kwargs["capture_output"] is True
        assert kwargs["text"] is True
        return SimpleNamespace(returncode=0, stdout="scan ok", stderr="")

    monkeypatch.setattr(container_scanning.shutil, "which", fake_which)
    monkeypatch.setattr(container_scanning.subprocess, "run", fake_run)

    result = scan_image_with_trivy(
        "ghcr.io/example/app:latest",
        skip_directories=[Path("/tmp/cache"), Path("/var/cache")],
        additional_args=["--timeout", "30"],
    )

    expected = [
        "/usr/bin/trivy",
        "image",
        "--no-progress",
        "--scanners",
        "vuln",
        "--format",
        "table",
        "--severity",
        ",".join(DEFAULT_SEVERITIES),
        "--vuln-type",
        "os,library",
        "--exit-code",
        "1",
        "--ignore-unfixed",
        "--skip-dirs",
        "/tmp/cache",
        "--skip-dirs",
        "/var/cache",
        "--timeout",
        "30",
        "ghcr.io/example/app:latest",
    ]
    assert commands["command"] == expected
    assert result.stdout == "scan ok"


def test_scan_image_raises_when_trivy_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(container_scanning.shutil, "which", lambda _: None)

    with pytest.raises(TrivyNotInstalledError):
        scan_image_with_trivy("example:latest")


def test_scan_image_raises_on_vulnerabilities(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(*args: object, **kwargs: object) -> SimpleNamespace:
        return SimpleNamespace(
            returncode=1,
            stdout="VULNERABILITIES FOUND",
            stderr="critical CVE-0000-0000",
        )

    monkeypatch.setattr(container_scanning.shutil, "which", lambda _: "/usr/bin/trivy")
    monkeypatch.setattr(container_scanning.subprocess, "run", fake_run)

    with pytest.raises(TrivyError) as excinfo:
        scan_image_with_trivy("example:latest")

    assert "Return code: 1" in str(excinfo.value)
    assert "VULNERABILITIES FOUND" in str(excinfo.value)


def test_cli_wrapper_passes_arguments(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    captured_kwargs: dict[str, object] = {}

    def fake_scan_image_with_trivy(
        image: str, **kwargs: object
    ) -> container_scanning.TrivyScanResult:
        captured_kwargs["image"] = image
        captured_kwargs.update(kwargs)
        return container_scanning.TrivyScanResult(
            image_ref=image,
            returncode=0,
            stdout="scan ok",
            stderr="",
        )

    monkeypatch.setattr(container_scanning, "scan_image_with_trivy", fake_scan_image_with_trivy)

    argv = [
        "ghcr.io/example/app:dev",
        "--severity",
        "CRITICAL",
        "HIGH",
        "--vuln-type",
        "os",
        "config",
        "--allow-findings",
        "--skip-dir",
        "/var/cache",
        "--extra-arg",
        "--cache-dir",
        "--extra-arg",
        "/tmp/trivy",
    ]

    container_scanning.main(argv)
    stdout = capsys.readouterr().out

    assert captured_kwargs["image"] == "ghcr.io/example/app:dev"
    assert captured_kwargs["severity"] == ("CRITICAL", "HIGH")
    assert captured_kwargs["vuln_types"] == ("os", "config")
    assert captured_kwargs["exit_on_findings"] is False
    assert captured_kwargs["ignore_unfixed"] is True
    assert captured_kwargs["skip_directories"] == [Path("/var/cache")]
    assert captured_kwargs["additional_args"] == ["--cache-dir", "/tmp/trivy"]
    assert "scan ok" in stdout


def test_scan_result_ensure_success_round_trip() -> None:
    result = container_scanning.TrivyScanResult(
        image_ref="example:latest",
        returncode=0,
        stdout="",
        stderr="",
    )

    assert result.ensure_success() is result


def test_scan_result_ensure_success_raises() -> None:
    result = container_scanning.TrivyScanResult(
        image_ref="example:latest",
        returncode=2,
        stdout="report",
        stderr="failure",
    )

    with pytest.raises(TrivyError):
        result.ensure_success()


def test_comma_join_rejects_empty_sequence() -> None:
    with pytest.raises(ValueError):
        container_scanning._comma_join(())  # type: ignore[attr-defined]


def test_build_command_without_ignore_unfixed() -> None:
    command = container_scanning._build_trivy_command(  # type: ignore[attr-defined]
        binary="/usr/bin/trivy",
        image_ref="example:latest",
        severity=("CRITICAL",),
        vuln_types=("os",),
        ignore_unfixed=False,
        exit_on_findings=False,
        skip_directories=None,
        additional_args=None,
    )

    assert "--ignore-unfixed" not in command
    assert command[-1] == "example:latest"
