from __future__ import annotations

import os
import re
import secrets
import shutil
import tempfile
from contextlib import AbstractContextManager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final

_ALLOWED_CHARS_PATTERN: Final[re.Pattern[str]] = re.compile(r"[^A-Za-z0-9._-]+")
_DEFAULT_PREFIX: Final[str] = "gabriel-task"


def _sanitize_identifier(identifier: str | None) -> str:
    """Return a filesystem-safe identifier for scratch directory names."""
    if identifier is None:
        return ""
    sanitized = _ALLOWED_CHARS_PATTERN.sub("-", identifier)
    return sanitized.strip("-_.")


def _ensure_within_base(path: Path, base: Path) -> None:
    """Raise ``ValueError`` when ``path`` escapes ``base``."""
    resolved_base = base.resolve()
    resolved_path = path.resolve(strict=False)
    if resolved_path == resolved_base:
        raise ValueError("Scratch path may not be the base directory itself")
    if not resolved_path.is_relative_to(resolved_base):
        raise ValueError(f"Scratch path {resolved_path} escapes base {resolved_base}")


@dataclass(slots=True)
class ScratchSpace(AbstractContextManager[Path]):
    """Context manager that provisions an isolated scratch directory."""

    task_id: str | None = None
    base_dir: Path | str | None = None
    prefix: str = _DEFAULT_PREFIX
    _directory_name: str = field(init=False)
    _base: Path = field(init=False)
    _path: Path = field(init=False)
    _active: bool = field(init=False, default=False)

    def __post_init__(self) -> None:
        base = Path(self.base_dir) if self.base_dir is not None else Path(tempfile.gettempdir())
        sanitized_identifier = _sanitize_identifier(self.task_id)
        if not sanitized_identifier:
            sanitized_identifier = secrets.token_hex(8)
        self._directory_name = f"{self.prefix}-{sanitized_identifier}"
        self._base = base.expanduser()
        self._path = (self._base / self._directory_name).resolve(strict=False)

    @property
    def path(self) -> Path:
        """Return the absolute path to the scratch directory."""
        return self._path

    def __enter__(self) -> Path:  # noqa: D401
        """Create the scratch directory and return its path."""
        self._prepare()
        return self._path

    def __exit__(self, exc_type, exc, exc_tb) -> None:  # noqa: D401
        """Remove the scratch directory on context exit."""
        self.cleanup()
        return None

    def cleanup(self) -> None:
        """Remove the scratch directory if it was created."""
        if not self._active:
            return
        if self._path.exists():
            _ensure_within_base(self._path, self._base)
            shutil.rmtree(self._path)
        self._active = False

    def _prepare(self) -> None:
        base = self._base
        if base.exists():
            if not base.is_dir():
                raise NotADirectoryError(f"Scratch base must be a directory: {base}")
        else:
            base.mkdir(parents=True, exist_ok=True)
        resolved_base = base.resolve()
        target = resolved_base / self._directory_name
        _ensure_within_base(target, resolved_base)
        if target.exists():
            if not target.is_dir():
                raise RuntimeError(f"Scratch path exists and is not a directory: {target}")
            shutil.rmtree(target)
        target.mkdir(mode=0o700)
        try:
            os.chmod(target, 0o700)
        except OSError:
            # Some filesystems do not support POSIX permissions (e.g., Windows FAT volumes).
            pass
        self._path = target
        self._active = True


def scratch_space(
    task_id: str | None = None,
    *,
    base_dir: Path | str | None = None,
    prefix: str = _DEFAULT_PREFIX,
) -> ScratchSpace:
    """Return a :class:`ScratchSpace` context manager with the desired configuration."""

    return ScratchSpace(task_id=task_id, base_dir=base_dir, prefix=prefix)


__all__ = [
    "ScratchSpace",
    "scratch_space",
]
