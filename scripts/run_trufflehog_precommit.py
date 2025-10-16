"""Utilities for running trufflehog against staged files in pre-commit."""

from __future__ import annotations

import argparse
import shutil
import subprocess  # nosec B404
import sys
import tempfile
from collections.abc import Sequence
from typing import Any

GIT_EXECUTABLE = shutil.which("git") or "git"


def run_git(
    args: Sequence[str],
    *,
    cwd: str | None = None,
    capture_output: bool = False,
    text: bool = True,
    **kwargs: Any,
) -> subprocess.CompletedProcess[str]:
    """Execute a git command and return the completed process."""

    if capture_output:
        kwargs.setdefault("stdout", subprocess.PIPE)
        kwargs.setdefault("stderr", subprocess.PIPE)
    return subprocess.run(  # nosec B603
        [GIT_EXECUTABLE, *args],
        cwd=cwd,
        check=True,
        text=text,
        **kwargs,
    )


def _has_staged_changes(repo_root: str) -> bool:
    """Return ``True`` when the git index contains staged changes."""

    result = run_git(
        ["diff", "--cached", "--name-only", "--diff-filter=ACMRT"],
        cwd=repo_root,
        capture_output=True,
    )
    return bool(result.stdout.strip())


def _prepare_snapshot_repo(repo_root: str) -> tuple[tempfile.TemporaryDirectory[str], bool]:
    """Create a temporary repository populated with the staged index contents."""

    temp_dir = tempfile.TemporaryDirectory()
    prefix = f"{temp_dir.name}/"
    run_git(["checkout-index", "--all", f"--prefix={prefix}"], cwd=repo_root)
    run_git(["init"], cwd=temp_dir.name, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    run_git(
        ["config", "user.name", "trufflehog-pre-commit"],
        cwd=temp_dir.name,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    run_git(
        ["config", "user.email", "trufflehog-pre-commit@example.com"],
        cwd=temp_dir.name,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    run_git(
        ["add", "--all"],
        cwd=temp_dir.name,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    status = run_git(
        ["status", "--porcelain"],
        cwd=temp_dir.name,
        capture_output=True,
    )
    if not status.stdout.strip():
        return temp_dir, False

    run_git(["commit", "--quiet", "-m", "pre-commit staged snapshot"], cwd=temp_dir.name)
    return temp_dir, True


def main(argv: list[str] | None = None) -> int:
    """Entry point for the trufflehog staged scan wrapper."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--trufflehog-bin",
        default="trufflehog",
        help="Executable used to invoke trufflehog.",
    )
    parser.add_argument(
        "trufflehog_args",
        nargs=argparse.REMAINDER,
        help="Arguments forwarded directly to trufflehog after '--'.",
    )
    args = parser.parse_args(argv)

    repo_root = run_git(
        ["rev-parse", "--show-toplevel"],
        capture_output=True,
    ).stdout.strip()

    if not _has_staged_changes(repo_root):
        return 0

    temp_repo, has_snapshot = _prepare_snapshot_repo(repo_root)

    if not has_snapshot:
        temp_repo.cleanup()
        return 0

    try:
        trufflehog_args = args.trufflehog_args or []
        if trufflehog_args and trufflehog_args[0] == "--":
            trufflehog_args = trufflehog_args[1:]
        trufflehog_executable = shutil.which(args.trufflehog_bin) or args.trufflehog_bin
        command = [trufflehog_executable, *trufflehog_args, "."]
        result = subprocess.run(command, cwd=temp_repo.name)  # nosec B603
        return result.returncode
    finally:
        temp_repo.cleanup()


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
