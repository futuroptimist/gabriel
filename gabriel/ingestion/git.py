"""Helpers for crawling Git repositories for commit metadata."""

from __future__ import annotations

import subprocess  # nosec B404
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

_GIT_LOG_SEPARATOR = "\x1f"


@dataclass(frozen=True, slots=True)
class CommitRecord:
    """Snapshot of a single Git commit."""

    sha: str
    author: str
    email: str | None
    date: datetime
    summary: str

    def to_dict(self) -> dict[str, str]:
        """Return a JSON-serialisable representation of the commit."""
        payload: dict[str, str] = {
            "sha": self.sha,
            "author": self.author,
            "date": self.date.isoformat(),
            "summary": self.summary,
        }
        if self.email is not None:
            payload["email"] = self.email
        return payload


@dataclass(frozen=True, slots=True)
class RepositoryCommits:
    """Commits collected from a Git repository."""

    path: Path
    commits: tuple[CommitRecord, ...]

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serialisable representation of the repository."""
        return {
            "path": str(self.path),
            "commits": [commit.to_dict() for commit in self.commits],
        }


def collect_repository_commits(
    paths: Iterable[Path | str],
    *,
    limit: int = 20,
    redact_emails: bool = False,
) -> list[RepositoryCommits]:
    """Collect commit metadata from each Git repository in ``paths``."""
    normalized_limit = max(limit, 0)
    summaries: list[RepositoryCommits] = []
    for raw_path in paths:
        path = _normalize_repository_path(raw_path)
        _ensure_git_repository(path)
        commits = _read_commits(path, normalized_limit, redact_emails=redact_emails)
        summaries.append(RepositoryCommits(path=path, commits=tuple(commits)))
    return summaries


def _normalize_repository_path(raw_path: Path | str) -> Path:
    path = Path(raw_path).expanduser()
    if not path.exists():
        raise FileNotFoundError(f"Repository path does not exist: {path}")
    if not path.is_dir():
        raise NotADirectoryError(f"Repository path must be a directory: {path}")
    return path.resolve()


def _ensure_git_repository(path: Path) -> None:
    try:
        result = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "--is-inside-work-tree"],
            check=False,
            capture_output=True,
            text=True,
        )  # nosec
    except FileNotFoundError as exc:  # pragma: no cover - depends on system git
        raise RuntimeError("Git executable is not available on PATH") from exc
    if result.returncode != 0 or result.stdout.strip() != "true":
        raise ValueError(f"Path is not a Git repository: {path}")


def _read_commits(
    path: Path, limit: int, *, redact_emails: bool = False
) -> list[CommitRecord]:
    if limit == 0:
        return []
    try:
        result = subprocess.run(
            [
                "git",
                "-C",
                str(path),
                "log",
                "-n",
                str(limit),
                "--date=iso-strict",
                "--pretty=format:%H%x1f%an%x1f%ae%x1f%aI%x1f%s",
            ],
            check=False,
            capture_output=True,
            text=True,
        )  # nosec
    except FileNotFoundError as exc:  # pragma: no cover - depends on system git
        raise RuntimeError("Git executable is not available on PATH") from exc

    if result.returncode != 0:
        stderr = result.stderr.strip()
        if "does not have any commits yet" in stderr:
            return []
        raise RuntimeError(f"Failed to read commits from {path}: {stderr}")

    commits: list[CommitRecord] = []
    for line in result.stdout.splitlines():
        if not line:
            continue
        fields = line.split(_GIT_LOG_SEPARATOR)
        if len(fields) != 5:
            continue
        sha, author, email, date_str, summary = (field.strip() for field in fields)
        parsed_date = datetime.fromisoformat(date_str)
        normalized_email: str | None = None
        if email and not redact_emails:
            normalized_email = email
        commits.append(
            CommitRecord(
                sha=sha,
                author=author,
                email=normalized_email,
                date=parsed_date,
                summary=summary,
            )
        )
    return commits


__all__ = [
    "CommitRecord",
    "RepositoryCommits",
    "collect_repository_commits",
]
