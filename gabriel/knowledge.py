"""Compatibility shim for ``gabriel.ingestion.knowledge``."""

from gabriel.ingestion.knowledge import *  # noqa: F401,F403

__all__ = [name for name in globals() if not name.startswith("_")]
