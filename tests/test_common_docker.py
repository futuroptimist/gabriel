from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any, cast

import pytest

from gabriel.common.docker import VolumeMount, run_in_disposable_container, volume_mount


def test_run_in_disposable_container_builds_command(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    recorded: dict[str, Any] = {}

    def fake_run(cmd: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        recorded["cmd"] = cmd
        recorded["kwargs"] = kwargs
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setattr(subprocess, "run", fake_run)

    workspace = tmp_path / "workspace"
    workspace.mkdir()

    mount = volume_mount(workspace, "/workspace", read_only=True)

    run_in_disposable_container(
        "python:3.11",
        ["python", "-m", "http.server"],
        volumes=[mount],
        environment={"MODE": "test"},
        workdir="/workspace",
        network="host",
        user="1000:1000",
        extra_args=["--cpus", "1"],
        capture_output=True,
        text=True,
    )

    command = cast(list[str], recorded["cmd"])
    assert command[:3] == ["docker", "run", "--rm"]
    assert command[3:5] == ["--cpus", "1"]
    assert "--network" in command
    assert "--user" in command
    assert "-w" in command

    env_index = command.index("-e")
    assert command[env_index + 1] == "MODE=test"

    volume_index = command.index("-v")
    assert command[volume_index + 1].endswith(":/workspace:ro")
    assert command[-4] == "python:3.11"
    assert command[-3:] == ["python", "-m", "http.server"]

    kwargs = cast(dict[str, Any], recorded["kwargs"])
    assert kwargs["capture_output"] is True
    assert kwargs["text"] is True
    assert kwargs["check"] is True


def test_run_in_disposable_container_accepts_string_command(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    recorded: dict[str, Any] = {}

    def fake_run(cmd: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        recorded["cmd"] = cmd
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setattr(subprocess, "run", fake_run)

    run_in_disposable_container("alpine:3.19", "echo hello")

    assert recorded["cmd"][-3:] == ["sh", "-c", "echo hello"]


def test_run_in_disposable_container_rejects_rm_override() -> None:
    with pytest.raises(ValueError, match="--rm is enforced automatically"):
        run_in_disposable_container("alpine:3.19", ["echo", "hello"], extra_args=["--rm"])


def test_volume_mount_accepts_plain_paths(tmp_path: Path) -> None:
    host_path = tmp_path / "data"
    host_path.mkdir()

    mount = VolumeMount(host_path=host_path, container_path="/data", read_only=False)
    _, spec = mount.to_argument()
    assert spec.startswith(str(host_path.resolve()))
    assert spec.endswith(":/data")


def test_run_in_disposable_container_requires_image() -> None:
    with pytest.raises(ValueError, match="image must be a non-empty"):
        run_in_disposable_container("   ", ["echo", "hi"])


def test_run_in_disposable_container_rejects_empty_command_string() -> None:
    with pytest.raises(ValueError, match="command string must contain"):
        run_in_disposable_container("alpine:3.19", "   ")


def test_run_in_disposable_container_allows_default_entrypoint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    recorded: dict[str, Any] = {}

    def fake_run(cmd: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        recorded["cmd"] = cmd
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setattr(subprocess, "run", fake_run)

    run_in_disposable_container("alpine:3.19")

    assert recorded["cmd"] == ["docker", "run", "--rm", "alpine:3.19"]


def test_run_in_disposable_container_validates_environment_keys() -> None:
    with pytest.raises(ValueError, match="environment variable names must be non-empty"):
        run_in_disposable_container("alpine:3.19", ["true"], environment={"": "value"})
