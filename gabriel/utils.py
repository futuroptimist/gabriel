"""Compatibility shim exposing the legacy CLI surface from :mod:`gabriel.ui.cli`."""

from __future__ import annotations

from .arithmetic import add, divide, floordiv, modulo, multiply, power, sqrt, subtract
from .secrets import delete_secret, get_secret, read_secret_from_input, store_secret
from .ui.cli import (
    SECRET_CMD_DELETE,
    SECRET_CMD_GET,
    SECRET_CMD_STORE,
    _env_secret_key,
    _read_secret_from_input,
    main,
)
from .ui.viewer import serve_viewer

__all__ = [
    "add",
    "subtract",
    "multiply",
    "divide",
    "power",
    "modulo",
    "floordiv",
    "sqrt",
    "store_secret",
    "get_secret",
    "delete_secret",
    "read_secret_from_input",
    "serve_viewer",
    "SECRET_CMD_STORE",
    "SECRET_CMD_GET",
    "SECRET_CMD_DELETE",
    "_env_secret_key",
    "_read_secret_from_input",
    "main",
]


if __name__ == "__main__":  # pragma: no cover - CLI entry point compatibility
    main()
