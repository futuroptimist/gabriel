"""Compatibility layer for legacy imports.

This module re-exports prompt sanitization helpers that now live under
:mod:`gabriel.ingestion.text`. Downstream callers should migrate to the new
module path to align with the four-module architecture.
"""

from __future__ import annotations

import importlib
from types import ModuleType

_target_module: ModuleType = importlib.import_module("gabriel.ingestion.text")

for _name in dir(_target_module):
    if _name.startswith("__"):
        continue
    globals()[_name] = getattr(_target_module, _name)

del _name

__all__ = getattr(_target_module, "__all__", []) or [
    name for name in globals() if not name.startswith("__") and name != "_target_module"
]

del _target_module

if __name__ == "__main__":  # pragma: no cover - legacy CLI compatibility
    maybe_main = globals().get("main")
    if callable(maybe_main):
        run_main = maybe_main
    else:
        from gabriel.ingestion.text import main as run_main

    raise SystemExit(run_main())
