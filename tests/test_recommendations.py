from __future__ import annotations

from gabriel.knowledge import Note
from gabriel.recommendations import (
    Recommendation,
    RiskTolerance,
    generate_recommendations,
)
from gabriel.selfhosted import CheckResult


def _note(identifier: str, title: str, content: str, *tags: str) -> Note:
    return Note(identifier=identifier, title=title, content=content, tags=tuple(tags))


def test_generate_recommendations_prioritizes_high_severity_and_includes_notes() -> None:
    findings = [
        CheckResult(
            slug="vaultwarden-https",
            message="VaultWarden should be served over HTTPS with a trusted certificate.",
            severity="high",
            remediation="Configure HTTPS for VaultWarden.",
        ),
        CheckResult(
            slug="syncthing-relays",
            message="Relay servers are enabled; disable relays when peers share trusted links.",
            severity="medium",
            remediation="Disable relay usage to keep traffic on trusted paths.",
        ),
    ]
    notes = [
        _note(
            "notes/vaultwarden.md",
            "VaultWarden Hardening",
            "Always enforce HTTPS using a trusted certificate authority.",
            "vaultwarden",
            "https",
        ),
        _note(
            "notes/vaultwarden-extended.md",
            "VaultWarden Extended Guidance",
            (
                "Ensure VaultWarden endpoints use TLS, rotate certificates quarterly, "
                "enforce strong admin tokens, and document backup recovery drills for "
                "the entire team while monitoring access logs."
            ),
            "tls",
        ),
        _note(
            "notes/networking.md",
            "Relay usage",
            "Relays are useful for remote peers but add latency and risk.",
            "syncthing",
        ),
    ]

    recommendations = generate_recommendations(
        findings=findings,
        knowledge_notes=notes,
        focus_tags=("vaultwarden",),
        risk_tolerance=RiskTolerance.LOW,
    )

    assert recommendations, "expected at least one recommendation"
    first = recommendations[0]
    assert isinstance(first, Recommendation)
    assert first.slug == "vaultwarden-https"
    assert "Guidance" in first.rationale
    assert "notes/vaultwarden.md" in first.sources
    assert first.score > recommendations[1].score


def test_generate_recommendations_respects_risk_tolerance() -> None:
    low_finding = CheckResult(
        slug="viewer-access",
        message="Viewer preview is exposed to the internet without authentication.",
        severity="low",
        remediation="Bind the viewer to localhost or require authentication.",
    )

    tolerant = generate_recommendations(
        findings=(low_finding,),
        risk_tolerance=RiskTolerance.HIGH,
    )
    assert tolerant == []

    strict = generate_recommendations(
        findings=(low_finding,),
        risk_tolerance=RiskTolerance.LOW,
    )
    assert strict and strict[0].slug == "viewer-access"


def test_generate_recommendations_merges_duplicate_slugs() -> None:
    duplicate = [
        CheckResult(
            slug="syncthing-relays",
            message="Relays introduce untrusted hops.",
            severity="medium",
            remediation="Disable relays when devices share a LAN.",
        ),
        CheckResult(
            slug="syncthing-relays",
            message="Relays can reveal metadata to third parties.",
            severity="high",
            remediation="Restrict relay usage to trusted networks only.",
        ),
        CheckResult(
            slug="syncthing-relays",
            message="Relays complicate troubleshooting when the direct path is healthy.",
            severity="medium",
            remediation="Prefer direct connections before enabling relay fallbacks.",
        ),
        CheckResult(
            slug="syncthing-relays",
            message="Relays can reveal metadata to third parties.",
            severity="high",
            remediation="Restrict relay usage to trusted networks only.",
        ),
    ]

    recommendations = generate_recommendations(findings=duplicate)

    assert len(recommendations) == 1
    combined = recommendations[0]
    assert combined.severity == "high"
    assert combined.summary == "Relays can reveal metadata to third parties."
    assert len(combined.remediation) == 3
    assert "Relays introduce untrusted hops." in combined.rationale


def test_generate_recommendations_honours_max_recommendations() -> None:
    findings = [
        CheckResult(
            slug="vaultwarden-https",
            message="VaultWarden should be served over HTTPS with a trusted certificate.",
            severity="high",
            remediation="Configure HTTPS for VaultWarden.",
        ),
        CheckResult(
            slug="vaultwarden-admin-network",
            message="Admin interface is reachable from untrusted networks.",
            severity="high",
            remediation="Restrict access to VPN ranges or internal subnets only.",
        ),
        CheckResult(
            slug="vaultwarden-backups",
            message="Backups run infrequently. Aim for at least daily snapshots.",
            severity="medium",
            remediation="Schedule automated backups at least once per day.",
        ),
    ]

    recommendations = generate_recommendations(
        findings=findings,
        knowledge_notes=(_note("notes/vw-empty.md", "VaultWarden Overview", "", "vaultwarden"),),
        focus_tags=("snapshot",),
        max_recommendations=1,
    )

    assert len(recommendations) == 1
    assert recommendations[0].slug in {"vaultwarden-https", "vaultwarden-admin-network"}
