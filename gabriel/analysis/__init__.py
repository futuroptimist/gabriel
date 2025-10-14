"""Security analysis primitives grouped under the Gabriel analysis module."""

from __future__ import annotations

from .phishing import (
    PhishingFinding,
    analyze_text_for_phishing,
    analyze_url,
    extract_urls,
)
from .policy import (
    PolicyValidationError,
    PolicyValidationResult,
    load_policy_document,
    validate_policy_document,
    validate_policy_file,
)
from .recommendations import Recommendation, RiskTolerance, generate_recommendations
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

__all__ = [
    "PhishingFinding",
    "analyze_text_for_phishing",
    "analyze_url",
    "extract_urls",
    "Recommendation",
    "RiskTolerance",
    "generate_recommendations",
    "CheckResult",
    "Severity",
    "DockerDaemonConfig",
    "VaultWardenConfig",
    "SyncthingConfig",
    "NextcloudConfig",
    "PhotoPrismConfig",
    "audit_docker_daemon",
    "audit_vaultwarden",
    "audit_syncthing",
    "audit_nextcloud",
    "audit_photoprism",
    "PolicyValidationError",
    "PolicyValidationResult",
    "load_policy_document",
    "validate_policy_document",
    "validate_policy_file",
]
