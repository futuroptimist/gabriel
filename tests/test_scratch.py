from __future__ import annotations

import os
import shutil
import stat
from pathlib import Path

import pytest

from gabriel.common.scratch import ScratchSpace, _ensure_within_base, scratch_space


def test_scratch_space_creates_directory_and_cleans_up(tmp_path):
    space = ScratchSpace(task_id="example", base_dir=tmp_path)
    expected_path = space.path
    assert expected_path.name.startswith("gabriel-task-")
    with space as path:
        assert path.exists()
        assert path.is_dir()
        assert path.parent == tmp_path.resolve()
        marker = path / "marker.txt"
        marker.write_text("hello", encoding="utf-8")
        if os.name == "posix":
            assert stat.S_IMODE(path.stat().st_mode) == 0o700
    assert not (path / "marker.txt").exists()
    assert not path.exists()
    # cleanup is idempotent even when directory already removed
    space.cleanup()


@pytest.mark.parametrize(
    "task_id",
    [
        "../bad spaces!!",
        "",
        None,
    ],
)
def test_scratch_space_sanitizes_identifier(task_id, tmp_path):
    with ScratchSpace(task_id=task_id, base_dir=tmp_path) as path:
        name = path.name
        assert name.startswith("gabriel-task-")
        suffix = name.removeprefix("gabriel-task-")
        assert suffix
        assert set(suffix) <= set(
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_"
        )
    assert not path.exists()


def test_scratch_space_wipes_existing_directory(tmp_path):
    task_id = "reuse"
    existing = tmp_path / "gabriel-task-reuse"
    existing.mkdir()
    stale = existing / "stale.txt"
    stale.write_text("old", encoding="utf-8")

    with ScratchSpace(task_id=task_id, base_dir=tmp_path) as path:
        assert path == existing.resolve()
        assert not (path / "stale.txt").exists()
        fresh = path / "fresh.txt"
        fresh.write_text("new", encoding="utf-8")
    assert not existing.exists()


def test_scratch_space_factory_helper(tmp_path):
    with scratch_space(task_id="factory", base_dir=tmp_path) as path:
        assert path.exists()
        assert path.is_dir()
    assert not path.exists()


def test_scratch_space_creates_base_directory(tmp_path):
    missing_base = tmp_path / "nested" / "scratch"
    with ScratchSpace(task_id="build", base_dir=missing_base) as path:
        assert missing_base.exists()
        assert missing_base.is_dir()
        assert path.parent == missing_base.resolve()
    assert not path.exists()


def test_scratch_space_rejects_non_directory_base(tmp_path):
    base_file = tmp_path / "base-file"
    base_file.write_text("not a directory", encoding="utf-8")
    with pytest.raises(NotADirectoryError):
        ScratchSpace(task_id="oops", base_dir=base_file).__enter__()


def test_scratch_space_rejects_existing_file_target(tmp_path):
    target = tmp_path / "gabriel-task-clash"
    target.write_text("collision", encoding="utf-8")
    with pytest.raises(RuntimeError):
        ScratchSpace(task_id="clash", base_dir=tmp_path).__enter__()


def test_scratch_space_handles_chmod_error(monkeypatch, tmp_path):
    def _raise_chmod_error(path: Path, mode: int) -> None:  # pragma: no cover - executed via test
        raise OSError("unsupported filesystem")

    monkeypatch.setattr("gabriel.common.scratch.os.chmod", _raise_chmod_error)
    with ScratchSpace(task_id="chmod", base_dir=tmp_path) as path:
        assert path.exists()
    assert not path.exists()


def test_cleanup_handles_missing_directory(tmp_path):
    space = ScratchSpace(task_id="missing", base_dir=tmp_path)
    with space as path:
        assert path.exists()
        shutil.rmtree(path)
        assert not path.exists()
    assert not space.path.exists()


def test_ensure_within_base_guards(tmp_path):
    with pytest.raises(ValueError):
        _ensure_within_base(tmp_path, tmp_path)

    outside = tmp_path.parent / "elsewhere"
    with pytest.raises(ValueError):
        _ensure_within_base(outside, tmp_path)
