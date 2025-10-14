"""Compatibility shim for ``gabriel.ingestion.text``."""

from gabriel.ingestion.text import *  # noqa: F401,F403

__all__ = [name for name in globals() if not name.startswith("_")]


if __name__ == "__main__":  # pragma: no cover - legacy CLI shim
    from gabriel.ingestion.text import main as _main

    raise SystemExit(_main())
