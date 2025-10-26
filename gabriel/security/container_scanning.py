"""Helpers for scanning container images with Trivy."""

from __future__ import annotations

import shutil
import subprocess  # nosec B404
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

DEFAULT_SEVERITIES: tuple[str, ...] = ("CRITICAL", "HIGH")
DEFAULT_VULN_TYPES: tuple[str, ...] = ("os", "library")


class TrivyError(RuntimeError):
    """Raised when a Trivy scan fails or the tool is not available."""


class TrivyNotInstalledError(TrivyError):
    """Raised when the Trivy binary cannot be located on ``PATH``."""


@dataclass(frozen=True)
class TrivyScanResult:
    """Result returned after invoking a Trivy scan."""

    image_ref: str
    returncode: int
    stdout: str
    stderr: str

    def ensure_success(self) -> TrivyScanResult:
        """Return ``self`` if the scan succeeded, otherwise raise :class:`TrivyError`."""

        if self.returncode != 0:
            raise TrivyError(
                "Trivy reported vulnerabilities or failed to scan the image."
                f" Return code: {self.returncode}. Stderr: {self.stderr.strip()}"
            )
        return self


def _comma_join(values: Sequence[str]) -> str:
    if not values:
        raise ValueError("At least one value must be provided.")
    return ",".join(values)


def _resolve_trivy() -> str:
    binary = shutil.which("trivy")
    if not binary:
        raise TrivyNotInstalledError(
            "Trivy executable not found on PATH. Install it or use setup-trivy-action in CI."
        )
    return binary


def _build_trivy_command(
    *,
    binary: str,
    image_ref: str,
    severity: Sequence[str] = DEFAULT_SEVERITIES,
    vuln_types: Sequence[str] = DEFAULT_VULN_TYPES,
    ignore_unfixed: bool = True,
    exit_on_findings: bool = True,
    skip_directories: Iterable[Path] | None = None,
    additional_args: Sequence[str] | None = None,
) -> list[str]:

    command = [
        binary,
        "image",
        "--no-progress",
        "--scanners",
        "vuln",
        "--format",
        "table",
        "--severity",
        _comma_join(tuple(severity)),
        "--vuln-type",
        _comma_join(tuple(vuln_types)),
        "--exit-code",
        "1" if exit_on_findings else "0",
    ]
    if ignore_unfixed:
        command.append("--ignore-unfixed")
    if skip_directories:
        for path in skip_directories:
            command.extend(["--skip-dirs", str(path)])
    if additional_args:
        command.extend(additional_args)
    command.append(image_ref)
    return command


def scan_image_with_trivy(
    image_ref: str,
    *,
    severity: Sequence[str] = DEFAULT_SEVERITIES,
    vuln_types: Sequence[str] = DEFAULT_VULN_TYPES,
    ignore_unfixed: bool = True,
    exit_on_findings: bool = True,
    skip_directories: Iterable[Path] | None = None,
    additional_args: Sequence[str] | None = None,
) -> TrivyScanResult:
    """Scan ``image_ref`` with Trivy and return the captured output."""

    binary = _resolve_trivy()
    command = _build_trivy_command(
        binary=binary,
        image_ref=image_ref,
        severity=severity,
        vuln_types=vuln_types,
        ignore_unfixed=ignore_unfixed,
        exit_on_findings=exit_on_findings,
        skip_directories=skip_directories,
        additional_args=additional_args,
    )

    completed = subprocess.run(  # noqa: S603,S607  # nosec B603
        command,
        check=False,
        capture_output=True,
        text=True,
    )
    result = TrivyScanResult(
        image_ref=image_ref,
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )
    if completed.returncode != 0:
        raise TrivyError(
            "Trivy reported vulnerabilities or failed to scan the image."
            f" Return code: {completed.returncode}."
            f"\nStdout: {completed.stdout.strip()}"
            f"\nStderr: {completed.stderr.strip()}"
        )
    return result


def main(argv: Sequence[str] | None = None) -> None:
    """Run the Trivy scan helper as a CLI tool."""

    import argparse

    parser = argparse.ArgumentParser(description="Scan container images with Trivy")
    parser.add_argument("image", help="Image reference to scan, e.g. ghcr.io/org/app:latest")
    parser.add_argument(
        "--severity",
        nargs="+",
        default=list(DEFAULT_SEVERITIES),
        help="List of severities to include (default: CRITICAL HIGH)",
    )
    parser.add_argument(
        "--vuln-type",
        nargs="+",
        default=list(DEFAULT_VULN_TYPES),
        help="Vulnerability types to include (default: os library)",
    )
    parser.add_argument(
        "--skip-dir",
        dest="skip_dirs",
        action="append",
        default=None,
        help="Additional directories inside the image to skip during scanning.",
    )
    parser.add_argument(
        "--include-unfixed",
        dest="ignore_unfixed",
        action="store_false",
        help="Include vulnerabilities without upstream fixes.",
    )
    parser.add_argument(
        "--allow-findings",
        dest="exit_on_findings",
        action="store_false",
        help="Return success even if vulnerabilities are found.",
    )
    parser.add_argument(
        "--extra-arg",
        dest="additional_args",
        action="append",
        nargs=1,
        default=None,
        metavar="ARG",
        help="Forward additional raw arguments to Trivy.",
    )
    args = parser.parse_args(argv)

    skip_dirs = [Path(value) for value in args.skip_dirs] if args.skip_dirs else None
    additional_args = (
        [item for group in args.additional_args for item in group]
        if args.additional_args
        else None
    )

    result = scan_image_with_trivy(
        args.image,
        severity=tuple(args.severity),
        vuln_types=tuple(args.vuln_type),
        ignore_unfixed=args.ignore_unfixed,
        exit_on_findings=args.exit_on_findings,
        skip_directories=skip_dirs,
        additional_args=additional_args,
    )
    print(result.stdout)


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()
