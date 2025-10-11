from __future__ import annotations

from pathlib import Path

import pytest

from gabriel import KnowledgeStore, Note, load_notes_from_paths
import gabriel.knowledge as knowledge_module


def _write(tmp_path: Path, name: str, content: str) -> Path:
    path = tmp_path / name
    path.write_text(content, encoding="utf-8")
    return path


def test_load_notes_from_paths_parses_front_matter(tmp_path: Path) -> None:
    vault = _write(
        tmp_path,
        "vaultwarden.md",
        """---
        title: VaultWarden hardening
        tags:
          - passwords
          - backups
        ---
        Rotate admin tokens quarterly and store them in the password manager.
        """,
    )
    syncthing = _write(
        tmp_path,
        "syncthing.md",
        """# Syncthing on LAN
        Disable global discovery and relays when devices share the same network.
        """,
    )

    notes = list(load_notes_from_paths([vault, syncthing]))

    assert {note.title for note in notes} == {
        "VaultWarden hardening",
        "Syncthing on LAN",
    }  # nosec B101
    vault_note = next(note for note in notes if "VaultWarden" in note.title)
    assert vault_note.tags == ("passwords", "backups")  # nosec B101
    assert "Rotate admin tokens" in vault_note.content  # nosec B101
    syncthing_note = next(note for note in notes if note.title.startswith("Syncthing"))
    assert syncthing_note.tags == ()  # nosec B101


def test_knowledge_store_search_ranks_matches(tmp_path: Path) -> None:
    configs = [
        Note(
            identifier="notes/vault.md",
            title="Vault backups",
            content=(
                "Before enabling remote sync tasks, administrators should confirm encrypted "
                "backups remain active across every node and schedule monthly restore drills."
            ),
            tags=("vaultwarden", "backups"),
        ),
        Note(
            identifier="notes/syncthing.md",
            title="Syncthing allow-list",
            content="Audit unknown device IDs and enforce TLS for the admin UI.",
            tags=("syncthing", "network"),
        ),
        Note(
            identifier="notes/checklist.md",
            title="General hardening",
            content="Enforce MFA, rotate credentials, and monitor admin logins.",
            tags=("mfa", "backups"),
        ),
    ]
    store = KnowledgeStore(configs)

    results = store.search("admin backups", required_tags=("backups",))

    assert [result.note.identifier for result in results] == [
        "notes/checklist.md",
        "notes/vault.md",
    ]  # nosec B101
    assert results[0].matched_terms == ("admin", "backups")  # nosec B101
    assert "admin" in results[0].snippet.lower()  # nosec B101


def test_knowledge_store_search_limit_and_empty_query(tmp_path: Path) -> None:
    store = KnowledgeStore(
        [
            Note(
                identifier="a",
                title="Rotations",
                content="Rotate passwords and API tokens every 90 days.",
                tags=("credentials",),
            ),
            Note(
                identifier="b",
                title="Alerts",
                content="Configure alerting on failed logins and brute force attempts.",
                tags=("monitoring",),
            ),
        ]
    )

    limited = store.search("rotate tokens logins", limit=1)
    assert len(limited) == 1  # nosec B101

    with pytest.raises(ValueError):
        store.search("   ")


def test_knowledge_store_from_paths_and_edge_cases(tmp_path: Path) -> None:
    (tmp_path / "subdir").mkdir()

    empty_note = tmp_path / "empty.md"
    empty_note.write_text("", encoding="utf-8")

    unfinished = tmp_path / "unfinished.md"
    unfinished.write_text(
        """---
title: Should be ignored
tags:
  - stray
Body line one.
Body line two.
""",
        encoding="utf-8",
    )

    meta_note = tmp_path / "meta.md"
    meta_note.write_text(
        """---
description:
  Keep backups

  after updates
aliases: alpha, beta
tags: security; backups
empty: []
---
# Operations briefing
First line describes admin dashboards in detail for the operations team.
Second line references audits and log reviews for compliance and retention policies.
Third line highlights internal runbooks and tabletop exercises for the response crew.
""",
        encoding="utf-8",
    )

    store = KnowledgeStore.from_paths(tmp_path.iterdir())
    identifiers = {note.identifier for note in store.notes}
    assert str(empty_note) in identifiers  # nosec B101
    assert str(unfinished) in identifiers  # nosec B101
    assert str(meta_note) in identifiers  # nosec B101
    assert len(store.notes) == 3  # directory was ignored  # nosec B101

    fallback_note = next(note for note in store.notes if note.identifier == str(unfinished))
    assert fallback_note.title == "---"  # front matter remained inline  # nosec B101
    empty_loaded = next(note for note in store.notes if note.identifier == str(empty_note))
    assert empty_loaded.title == "empty"  # fallback to stem  # nosec B101
    meta_loaded = next(note for note in store.notes if note.identifier == str(meta_note))
    assert meta_loaded.tags == ("security", "backups")  # nosec B101

    assert store.search("nonexistent keyword") == []  # nosec B101
    assert store.search("empty", limit=0) == []  # limit branch  # nosec B101

    empty_result = store.search("empty")[0]
    assert empty_result.snippet == ""  # nosec B101

    preview_result = store.search("security")[0]
    assert "admin dashboards" in preview_result.snippet  # nosec B101
    assert "security" not in preview_result.snippet.lower()  # preview branch  # nosec B101


def test_internal_helpers_cover_branches() -> None:
    block = """description:\n  keep\n\n  going\naliases: alpha, beta\n"""
    metadata = knowledge_module._parse_simple_front_matter(block)
    assert metadata["description"] == "keep, going"  # nosec B101
    assert metadata["aliases"] == "alpha, beta"  # nosec B101

    list_block = """tags:\n  - alpha\n  - beta\n"""
    list_metadata = knowledge_module._parse_simple_front_matter(list_block)
    assert list_metadata["tags"] == "alpha, beta"  # nosec B101

    assert knowledge_module._normalize_value("alpha, beta") == "alpha, beta"  # nosec B101

    heading = knowledge_module._derive_title("# Heading\nbody", fallback="fallback")
    assert heading == "Heading"  # nosec B101
    first_line = knowledge_module._derive_title("\nFirst line\nSecond", fallback="fallback")
    assert first_line == "First line"  # nosec B101

    empty_preview = knowledge_module._build_snippet(Note("id", "title", "", ()), ("term",))
    assert empty_preview == ""  # nosec B101

    short_snippet = knowledge_module._build_snippet(
        Note("short", "Short", "Brief content mentions audit.", ()),
        ("audit",),
    )
    assert short_snippet.startswith("Brief content")  # nosec B101

    long_content = (
        "Content starts by highlighting incident response playbooks and then continues with "
        "additional guidance that easily exceeds eighty characters for preview testing."
    )
    preview_note = Note("preview", "Preview", long_content, ())
    preview = knowledge_module._build_snippet(preview_note, ("missing",))
    assert preview.endswith("...")  # nosec B101

    short_preview_note = Note("short-preview", "Short", "Small body without keyword.", ())
    short_preview = knowledge_module._build_snippet(short_preview_note, ("absent",))
    assert not short_preview.endswith("...")  # nosec B101
