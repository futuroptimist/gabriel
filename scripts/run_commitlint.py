"""Run commitlint across branch commits in local and CI environments."""

from __future__ import annotations

import subprocess  # nosec B404
import sys
from typing import Final


def _run_git(*args: str) -> subprocess.CompletedProcess[str]:
    """Run a git command and return the completed process."""

    return subprocess.run(  # nosec B603
        ("git", *args),
        check=False,
        capture_output=True,
        text=True,
    )


def _fetch_main() -> None:
    """Fetch the latest main branch, ignoring failures on shallow clones."""

    fetch_cmd: Final[tuple[str, ...]] = ("fetch", "origin", "main", "--depth", "100")
    result = _run_git(*fetch_cmd)
    if result.returncode != 0:
        sys.stderr.write("Warning: unable to fetch origin/main; continuing with local history.\n")


def _determine_base() -> str:
    """Determine the commit to compare against for commitlint."""

    for command in (
        ("merge-base", "origin/main", "HEAD"),
        ("merge-base", "main", "HEAD"),
        ("rev-parse", "HEAD^"),
    ):
        result = _run_git(*command)
        candidate = result.stdout.strip()
        if result.returncode == 0 and candidate:
            return candidate
    raise RuntimeError("Unable to determine a base commit for commitlint")


def main() -> int:
    """Execute commitlint using the locally installed CLI."""

    _fetch_main()
    if _run_git("rev-parse", "--verify", "origin/main").returncode != 0:
        sys.stderr.write("Warning: origin/main unavailable; skipping commitlint.\n")
        return 0
    try:
        base_commit = _determine_base()
    except RuntimeError as error:  # pragma: no cover - defensive guardrail
        sys.stderr.write(f"{error}\n")
        return 1

    result = subprocess.run(  # nosec B603
        (
            "npx",
            "--yes",
            "commitlint",
            "--from",
            base_commit,
            "--to",
            "HEAD",
        ),
        check=False,
    )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
