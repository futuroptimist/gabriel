#!/usr/bin/env python3
"""Run the lychee link checker with repository defaults."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess  # nosec B404
from pathlib import Path

LYCHEE_VERSION = "0.15.1"
CONFIG_PATH = Path("lychee.toml")


def _ensure_cargo_bin_on_path() -> None:
    """Ensure Cargo's binary directory is available on ``PATH`` when present."""

    cargo_bin = Path.home() / ".cargo" / "bin"
    if not cargo_bin.exists():
        return
    path = os.environ.get("PATH", "")
    parts = path.split(os.pathsep) if path else []
    if str(cargo_bin) not in parts:
        os.environ["PATH"] = os.pathsep.join([str(cargo_bin), *parts])


def _ensure_lychee_installed() -> None:
    """Install the ``lychee`` CLI when it is missing from the system."""

    _ensure_cargo_bin_on_path()
    if shutil.which("lychee"):
        return

    cargo = shutil.which("cargo")
    if not cargo:
        raise SystemExit(
            "cargo is required to install lychee. Install Rust or add lychee to your PATH."
        )

    install_cmd = [
        cargo,
        "install",
        "lychee",
        "--locked",
        "--version",
        LYCHEE_VERSION,
    ]
    subprocess.run(install_cmd, check=True)  # nosec B603
    _ensure_cargo_bin_on_path()
    if not shutil.which("lychee"):
        raise SystemExit("lychee installation completed but binary not found on PATH")


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    """Parse command-line arguments for link checking."""

    parser = argparse.ArgumentParser(description="Run lychee with repository defaults")
    parser.add_argument("paths", nargs="*", help="Files or directories to scan")
    return parser.parse_args(argv)


def _collect_targets(raw: list[str]) -> list[str]:
    """Return canonical paths to scan, falling back to project defaults."""

    if raw:
        targets: list[str] = []
        for item in raw:
            path = Path(item)
            if not path.exists():
                continue
            targets.append(str(path))
        if targets:
            return sorted(set(targets))

    defaults = ["README.md", "docs"]
    return [str(Path(item)) for item in defaults if Path(item).exists()]


def main(argv: list[str] | None = None) -> int:
    """Execute lychee with repository defaults and return the exit status."""

    args = _parse_args(argv)
    targets = _collect_targets(args.paths)
    if not targets:
        print("No markdown paths to scan.")
        return 0

    _ensure_lychee_installed()

    command = [
        "lychee",
        "--config",
        str(CONFIG_PATH),
        "--no-progress",
        "--verbose",
        "--accept",
        "200,429",
        *targets,
    ]

    try:
        subprocess.run(command, check=True)  # nosec B603
    except subprocess.CalledProcessError as exc:
        return exc.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
