"""Compatibility shim for ``gabriel.analysis.selfhosted``."""

from gabriel.analysis.selfhosted import *  # noqa: F401,F403

__all__ = [name for name in globals() if not name.startswith("_")]
