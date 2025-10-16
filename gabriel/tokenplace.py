"""Compatibility shims for the token.place relay adapters.

This module preserves the historical ``gabriel.tokenplace`` import path while the
notification adapters finish migrating into :mod:`gabriel.notify`. Downstream
callers should prefer :mod:`gabriel.notify.tokenplace` going forward.
"""

from __future__ import annotations

from warnings import warn

from gabriel.notify.tokenplace import (  # noqa: F401 - re-exported API surface
    TokenPlaceClient,
    TokenPlaceCompletion,
    TokenPlaceError,
    _load_egress_policy,
    _reset_egress_policy_cache,
)
from gabriel.security.policies import EgressControlPolicy  # noqa: F401 - shim export

warn(
    "`gabriel.tokenplace` is deprecated; import from `gabriel.notify.tokenplace` instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "TokenPlaceClient",
    "TokenPlaceCompletion",
    "TokenPlaceError",
    "EgressControlPolicy",
    "_load_egress_policy",
    "_reset_egress_policy_cache",
]
