"""Helpers for executing commands in disposable Docker containers."""

from __future__ import annotations

# docker CLI invocation is controlled by validated arguments below
import subprocess  # nosec B404
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class VolumeMount:
    """Represents a single Docker volume mount specification."""

    host_path: Path
    container_path: str
    read_only: bool = False

    def __post_init__(self) -> None:  # pragma: no cover - dataclass boilerplate
        """Normalize the host path to an absolute ``Path``."""
        host_path = Path(self.host_path).expanduser()
        object.__setattr__(self, "host_path", host_path)

    def to_argument(self) -> tuple[str, str]:
        """Return the ``docker run`` argument tuple for the volume."""

        host = str(self.host_path.resolve(strict=False))
        spec = f"{host}:{self.container_path}"
        if self.read_only:
            spec += ":ro"
        return "-v", spec


def volume_mount(
    host_path: str | Path,
    container_path: str,
    *,
    read_only: bool = False,
) -> VolumeMount:
    """Create a :class:`VolumeMount` from host and container paths."""

    return VolumeMount(
        host_path=Path(host_path), container_path=container_path, read_only=read_only
    )


def _normalize_command(command: Sequence[str] | str | None) -> list[str]:
    if command is None:
        return []
    if isinstance(command, str):
        stripped = command.strip()
        if not stripped:
            raise ValueError("command string must contain executable content")
        return ["sh", "-c", stripped]
    return list(command)


def _normalize_environment(environment: Mapping[str, str] | None) -> list[str]:
    if not environment:
        return []
    arguments: list[str] = []
    for key, value in environment.items():
        key_str = str(key).strip()
        if not key_str:
            raise ValueError("environment variable names must be non-empty")
        arguments.extend(["-e", f"{key_str}={value}"])
    return arguments


def _normalize_volumes(volumes: Iterable[VolumeMount] | None) -> list[str]:
    if not volumes:
        return []
    arguments: list[str] = []
    for volume in volumes:
        arguments.extend(volume.to_argument())
    return arguments


def run_in_disposable_container(
    image: str,
    command: Sequence[str] | str | None = None,
    *,
    volumes: Iterable[VolumeMount] | None = None,
    environment: Mapping[str, str] | None = None,
    workdir: str | Path | None = None,
    network: str | None = None,
    user: str | None = None,
    extra_args: Sequence[str] | None = None,
    check: bool = True,
    capture_output: bool = False,
    text: bool = False,
    input: bytes | str | None = None,
    timeout: float | None = None,
) -> subprocess.CompletedProcess[bytes] | subprocess.CompletedProcess[str]:
    """Execute ``command`` in a transient Docker container derived from ``image``."""

    image_name = image.strip()
    if not image_name:
        raise ValueError("image must be a non-empty Docker image reference")

    run_args: list[str] = ["docker", "run", "--rm"]

    if extra_args:
        for argument in extra_args:
            if argument == "--rm" or argument.startswith("--rm="):
                raise ValueError("--rm is enforced automatically and must not be supplied")
        run_args.extend(extra_args)

    if network:
        run_args.extend(["--network", network])
    if user:
        run_args.extend(["--user", user])
    if workdir:
        run_args.extend(["-w", str(workdir)])

    run_args.extend(_normalize_environment(environment))
    run_args.extend(_normalize_volumes(volumes))
    run_args.append(image_name)
    run_args.extend(_normalize_command(command))

    result = subprocess.run(
        run_args,
        check=check,
        capture_output=capture_output,
        text=text,
        input=input,
        timeout=timeout,
    )  # nosec
    return result  # noqa: S603, S607 - docker is required for container execution


__all__ = ["run_in_disposable_container", "VolumeMount", "volume_mount"]
