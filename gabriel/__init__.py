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
from .ingestion.text import sanitize_prompt
from .knowledge import KnowledgeStore, Note, SearchResult, load_notes_from_paths
from .phishing import (
    PhishingFinding,
    analyze_text_for_phishing,
    analyze_url,
    extract_urls,
)
from .recommendations import Recommendation, RiskTolerance, generate_recommendations
from .secrets import delete_secret, get_secret, store_secret
from .selfhosted import (
    CheckResult,
    DockerDaemonConfig,
    NextcloudConfig,
    PhotoPrismConfig,
    Severity,
    SyncthingConfig,
    VaultWardenConfig,
    audit_docker_daemon,
    audit_nextcloud,
    audit_photoprism,
    audit_syncthing,
    audit_vaultwarden,
)
from .tokenplace import TokenPlaceClient, TokenPlaceCompletion, TokenPlaceError
from .ui import (
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
    "load_notes_from_paths",
    "KnowledgeStore",
    "Note",
    "SearchResult",
    "extract_urls",
    "analyze_url",
    "analyze_text_for_phishing",
    "PhishingFinding",
    "generate_recommendations",
    "Recommendation",
    "RiskTolerance",
    "DockerDaemonConfig",
    "VaultWardenConfig",
    "SyncthingConfig",
    "NextcloudConfig",
    "PhotoPrismConfig",
    "CheckResult",
    "Severity",
    "audit_docker_daemon",
    "audit_vaultwarden",
    "audit_syncthing",
    "audit_nextcloud",
    "audit_photoprism",
    "TokenPlaceClient",
    "TokenPlaceCompletion",
    "TokenPlaceError",
    "sanitize_prompt",
    "SUPPORTED_PYTHON_VERSIONS",
    "serve_viewer",
    "start_viewer_server",
    "ViewerServer",
    "DEFAULT_HOST",
    "DEFAULT_PORT",
]
