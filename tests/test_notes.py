from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest

from gabriel.notes import NoteDocument, NoteIndex, index_security_notes


def _write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def test_index_from_directory_and_search(tmp_path: Path) -> None:
    notes_dir = tmp_path / "notes"
    notes_dir.mkdir()
    vaultwarden = notes_dir / "vaultwarden.md"
    photoprism = notes_dir / "photoprism.txt"
    archive = notes_dir / "archive"
    archive.mkdir()
    misc = archive / "misc.rst"

    _write(
        vaultwarden,
        "\n".join(
            [
                "VaultWarden Hardening",
                "",
                "Require two-factor authentication for every account.",
                "Set the DOMAIN value to your public URL.",
                "Rotate the admin token frequently.",
                "",
            ]
        ),
    )
    _write(
        photoprism,
        "\n".join(
            [
                "PhotoPrism Notes",
                "",
                "Disable anonymous uploads.",
                "Prefer S3-compatible storage with versioning.",
                "",
            ]
        ),
    )
    _write(
        misc,
        "\n".join(
            [
                "Backups",
                "",
                "Keep encrypted snapshots of both services and test restores monthly.",
                "",
            ]
        ),
    )

    index = NoteIndex.from_directory(notes_dir)
    assert len(index.documents) == 3  # nosec B101

    results = index.search("vaultwarden domain")
    assert results  # nosec B101
    assert results[0].document.path == vaultwarden  # nosec B101
    if len(results) > 1:
        assert results[0].score >= results[1].score  # nosec B101

    title_match = index.search("VaultWarden Hardening")
    assert title_match[0].document.path == vaultwarden  # nosec B101

    content_match = index.search("anonymous uploads")
    assert content_match[0].document.path == photoprism  # nosec B101

    fuzzy = index.search("photo prism uploads", limit=2)
    assert fuzzy  # nosec B101
    assert photoprism == fuzzy[0].document.path  # nosec B101


def test_index_security_notes_wrapper(tmp_path: Path) -> None:
    note = tmp_path / "security.md"
    _write(note, "Security Checklist\n\nAudit secrets quarterly.")
    index = index_security_notes(tmp_path)
    [match] = index.search("secrets")
    assert match.document.path == note  # nosec B101


@pytest.mark.parametrize("query", ["", "   "])
def test_search_rejects_blank_query(query: str, tmp_path: Path) -> None:
    note = tmp_path / "note.md"
    _write(note, "Example note")
    index = index_security_notes(tmp_path)
    with pytest.raises(ValueError):
        index.search(query)


def test_binary_files_are_skipped(tmp_path: Path) -> None:
    (tmp_path / "note.md").write_bytes(b"plain text\n")
    (tmp_path / "image.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    index = index_security_notes(tmp_path)
    assert len(index.documents) == 1  # nosec B101


def test_limit_zero_returns_all_results(tmp_path: Path) -> None:
    note = tmp_path / "log.txt"
    _write(note, "Investigation Log\n\nVaultWarden domain mismatch.")
    index = index_security_notes(tmp_path)
    results = index.search("vaultwarden", limit=0)
    assert len(results) == 1  # nosec B101


def test_document_helpers_cover_edge_cases(tmp_path: Path) -> None:
    empty_note = tmp_path / "empty.md"
    _write(empty_note, "")
    doc = NoteDocument.from_path(empty_note)
    assert doc.title == "empty"  # nosec B101

    binary_note = tmp_path / "binary.md"
    binary_note.write_bytes(b"\x00\x01text")
    index = index_security_notes(tmp_path)
    assert all(match.document.path != binary_note for match in index.search("text"))  # nosec B101


def test_truncation_respects_max_bytes(tmp_path: Path) -> None:
    note = tmp_path / "long.md"
    _write(note, "Heading\n" + "a" * 20)
    doc = NoteDocument.from_path(note, max_bytes=10)
    assert len(doc.content) <= 10  # nosec B101
    index = index_security_notes(tmp_path, max_bytes=5)
    assert len(index.documents[0].content) <= 5  # nosec B101


def test_duplicate_patterns_do_not_duplicate_files(tmp_path: Path) -> None:
    note = tmp_path / "single.md"
    _write(note, "Checklist")
    index = index_security_notes(tmp_path, patterns=("*.md", "*.md"))
    assert len(index.documents) == 1  # nosec B101


def test_unreadable_file_is_skipped(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    note = tmp_path / "blocked.md"
    _write(note, "Secret")

    original_open: Callable[..., object] = Path.open

    def fake_open(self: Path, *args, **kwargs):
        if self == note:
            raise OSError("denied")
        return original_open(self, *args, **kwargs)

    monkeypatch.setattr(Path, "open", fake_open)

    index = index_security_notes(tmp_path)
    assert not index.documents  # nosec B101


def test_search_filters_zero_score(tmp_path: Path) -> None:
    note = tmp_path / "1234.md"
    _write(note, "Numbers only")
    index = index_security_notes(tmp_path)
    assert not index.search("abc")  # nosec B101
