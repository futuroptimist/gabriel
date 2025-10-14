"""Compatibility shim for ``gabriel.common.secrets``."""

from gabriel.common.secrets import *  # noqa: F401,F403

__all__ = [name for name in globals() if not name.startswith("_")]
