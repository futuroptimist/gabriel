from __future__ import annotations

import json
import subprocess
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

import pytest

import gabriel.ingestion.git as git_module
from gabriel.ingestion.git import collect_repository_commits
from gabriel.ui import cli as cli_module


def _init_repository(path: Path) -> None:
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "config", "user.name", "Gabriel Bot"],
        cwd=path,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "bot@example.com"],
        cwd=path,
        check=True,
        capture_output=True,
        text=True,
    )


def _commit_file(path: Path, name: str, content: str, message: str) -> None:
    file_path = path / name
    file_path.write_text(content, encoding="utf-8")
    subprocess.run(["git", "add", name], cwd=path, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "commit", "-m", message],
        cwd=path,
        check=True,
        capture_output=True,
        text=True,
    )


def test_collect_repository_commits_returns_metadata(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repository(repo)
    _commit_file(repo, "README.md", "hello", "Initial commit")
    _commit_file(repo, "notes.txt", "details", "Add notes")

    summaries = collect_repository_commits([repo], limit=5)
    assert len(summaries) == 1

    summary = summaries[0]
    assert summary.path == repo.resolve()
    assert len(summary.commits) == 2

    latest = summary.commits[0]
    assert latest.summary == "Add notes"
    assert latest.author == "Gabriel Bot"
    assert latest.email == "bot@example.com"
    assert latest.sha

    as_dict = summary.to_dict()
    assert as_dict["commits"][0]["email"] == "bot@example.com"


def test_cli_crawl_outputs_json_and_respects_redaction(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repository(repo)
    _commit_file(repo, "file.txt", "content", "Add file")

    output_file = tmp_path / "crawl.json"
    buffer = StringIO()
    with redirect_stdout(buffer):
        cli_module.main(
            [
                "crawl",
                str(repo),
                "--limit",
                "1",
                "--redact-emails",
                "--output",
                str(output_file),
            ]
        )

    payload = json.loads(buffer.getvalue())
    assert len(payload) == 1
    [entry] = payload
    assert entry["path"] == str(repo.resolve())
    assert len(entry["commits"]) == 1
    commit = entry["commits"][0]
    assert commit["summary"] == "Add file"
    assert "email" not in commit
    assert commit["author"] == "Gabriel Bot"

    written = json.loads(output_file.read_text(encoding="utf-8"))
    assert written == payload


def test_cli_crawl_exits_on_invalid_repository(tmp_path: Path) -> None:
    bogus = tmp_path / "missing"
    with pytest.raises(SystemExit) as excinfo:
        cli_module.main(["crawl", str(bogus)])
    assert "does not exist" in str(excinfo.value)


def test_collect_repository_commits_invalid_inputs(tmp_path: Path) -> None:
    missing = tmp_path / "missing"
    with pytest.raises(FileNotFoundError):
        collect_repository_commits([missing])

    file_path = tmp_path / "not-a-dir.txt"
    file_path.write_text("noop", encoding="utf-8")
    with pytest.raises(NotADirectoryError):
        collect_repository_commits([file_path])

    not_repo = tmp_path / "not-repo"
    not_repo.mkdir()
    with pytest.raises(ValueError):
        collect_repository_commits([not_repo])


def test_collect_repository_commits_zero_limit(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repository(repo)
    _commit_file(repo, "file.txt", "content", "Add file")

    summaries = collect_repository_commits([repo], limit=0)
    assert summaries[0].commits == ()


def test_collect_repository_commits_empty_repository(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repository(repo)

    summaries = collect_repository_commits([repo], limit=5)
    assert summaries[0].commits == ()


def test_collect_repository_commits_skips_malformed_lines(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    class DummyResult:
        def __init__(self, stdout: str, returncode: int = 0, stderr: str = "") -> None:
            self.stdout = stdout
            self.returncode = returncode
            self.stderr = stderr

    def fake_run(command: list[str], *, check: bool, capture_output: bool, text: bool):
        if command[3] == "rev-parse":
            return DummyResult(stdout="true\n")
        if command[3] == "log":
            stdout = "\nmalformed\n"
            stdout += "sha123\x1fAuthor\x1fauthor@example.com\x1f2024-01-01T00:00:00+00:00\x1fSubject\n"
            return DummyResult(stdout=stdout)
        raise AssertionError(f"Unexpected git command: {command}")

    monkeypatch.setattr(git_module.subprocess, "run", fake_run)

    summaries = collect_repository_commits([repo], limit=5)
    [summary] = summaries
    assert len(summary.commits) == 1
    commit = summary.commits[0]
    assert commit.summary == "Subject"
    assert commit.email == "author@example.com"


def test_collect_repository_commits_git_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    class DummyResult:
        def __init__(self, stdout: str, stderr: str, returncode: int) -> None:
            self.stdout = stdout
            self.stderr = stderr
            self.returncode = returncode

    def fake_run(command: list[str], *, check: bool, capture_output: bool, text: bool):
        if command[3] == "rev-parse":
            return DummyResult(stdout="true\n", stderr="", returncode=0)
        if command[3] == "log":
            return DummyResult(stdout="", stderr="fatal: unexpected error", returncode=1)
        raise AssertionError(f"Unexpected git command: {command}")

    monkeypatch.setattr(git_module.subprocess, "run", fake_run)

    with pytest.raises(RuntimeError) as excinfo:
        collect_repository_commits([repo])
    assert "Failed to read commits" in str(excinfo.value)


def test_cli_crawl_without_output_file(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repository(repo)
    _commit_file(repo, "file.txt", "content", "Add file")

    buffer = StringIO()
    with redirect_stdout(buffer):
        cli_module.main(["crawl", str(repo), "--limit", "1"])

    payload = json.loads(buffer.getvalue())
    commit = payload[0]["commits"][0]
    assert commit["email"] == "bot@example.com"
