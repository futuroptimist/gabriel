"""Core utilities for the Gabriel project."""

from __future__ import annotations

from .__about__ import (
    __author__,
    __keywords__,
    __license__,
    __summary__,
    __uri__,
    __version__,
)
from .arithmetic import add, divide, floordiv, modulo, multiply, power, sqrt, subtract
from .phishing import (
    PhishingFinding,
    analyze_text_for_phishing,
    analyze_url,
    extract_urls,
)
from .secrets import delete_secret, get_secret, store_secret
from .selfhosted import (
    CheckResult,
    NextcloudConfig,
    Severity,
    SyncthingConfig,
    VaultWardenConfig,
    audit_nextcloud,
    audit_syncthing,
    audit_vaultwarden,
)
from .viewer import (
    DEFAULT_HOST,
    DEFAULT_PORT,
    ViewerServer,
    serve_viewer,
    start_viewer_server,
)

SUPPORTED_PYTHON_VERSIONS = ("3.10", "3.11")

__all__ = [
    "__version__",
    "__summary__",
    "__uri__",
    "__author__",
    "__license__",
    "__keywords__",
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
    "extract_urls",
    "analyze_url",
    "analyze_text_for_phishing",
    "PhishingFinding",
    "VaultWardenConfig",
    "SyncthingConfig",
    "NextcloudConfig",
    "CheckResult",
    "Severity",
    "audit_vaultwarden",
    "audit_syncthing",
    "audit_nextcloud",
    "SUPPORTED_PYTHON_VERSIONS",
    "serve_viewer",
    "start_viewer_server",
    "ViewerServer",
    "DEFAULT_HOST",
    "DEFAULT_PORT",
]
