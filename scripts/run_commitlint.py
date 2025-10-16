"""Simplified Conventional Commit linter used by CI."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ALLOWED_TYPES = {
    "build",
    "chore",
    "ci",
    "docs",
    "feat",
    "fix",
    "perf",
    "refactor",
    "revert",
    "style",
    "test",
}

COMMIT_PATTERN = re.compile(
    r"^(?P<type>[a-z]+)(?P<scope>\([^)]+\))?: (?P<subject>.+)$",
    flags=re.MULTILINE,
)

ALLOWLIST_PATH = Path("scripts/commitlint_allowlist.txt")


def _run_git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args], encoding="utf-8", stderr=subprocess.DEVNULL
    ).strip()


def _load_allowlist(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return {
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }


def _commit_range(base_ref: str) -> list[str]:
    commits = _run_git("rev-list", "--reverse", f"{base_ref}..HEAD")
    return [commit for commit in commits.splitlines() if commit]


def _guess_base_ref() -> str:
    for candidate in (("origin/main",), ("main",)):
        try:
            return _run_git("merge-base", *candidate, "HEAD")
        except subprocess.CalledProcessError:
            continue
    return _run_git("rev-parse", "HEAD^")


def _validate_commit(sha: str, message: str) -> tuple[bool, str]:
    if message.startswith("Merge "):
        return True, ""
    match = COMMIT_PATTERN.match(message)
    if not match:
        return False, "commit message must follow '<type>: <subject>'"
    commit_type = match.group("type")
    subject = match.group("subject").strip()
    if commit_type not in ALLOWED_TYPES:
        return False, f"unknown commit type '{commit_type}'"
    if not subject:
        return False, "subject may not be empty"
    return True, ""


def _read_commit_message(sha: str) -> str:
    return _run_git("log", "-1", "--pretty=%B", sha).splitlines()[0]


def main() -> int:
    allowlist = _load_allowlist(ALLOWLIST_PATH)
    base_ref = _guess_base_ref()
    commits = _commit_range(base_ref)
    if not commits:
        print("No commits to lint; skipping.")
        return 0

    failures: list[str] = []
    for sha in commits:
        if sha in allowlist:
            continue
        message = _read_commit_message(sha)
        ok, reason = _validate_commit(sha, message)
        if not ok:
            failures.append(f"{sha[:7]}: {reason} (message: {message!r})")

    if failures:
        print("Commit linting failed:")
        for failure in failures:
            print(f" - {failure}")
        return 1

    print("All commit messages satisfy Conventional Commit requirements.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
