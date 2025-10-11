"""Utilities for indexing and searching personal security notes."""

from __future__ import annotations

import re
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path

_WORD_PATTERN = re.compile(r"[A-Za-z0-9]+")


@dataclass(frozen=True, slots=True)
class Note:
    """Represents a single note tracked by the knowledge store."""

    identifier: str
    title: str
    content: str
    tags: tuple[str, ...] = ()
    path: Path | None = None

    def iter_tokens(self) -> Iterator[str]:
        """Yield normalized tokens derived from the title, tags, and content."""

        for source in (self.title, " ".join(self.tags), self.content):
            for match in _WORD_PATTERN.finditer(source):
                yield match.group(0).lower()

    def matches_tags(self, tags: Sequence[str]) -> bool:
        """Return ``True`` when all ``tags`` are present on the note."""

        if not tags:
            return True
        normalized = {tag.lower() for tag in self.tags}
        return all(tag.lower() in normalized for tag in tags)


@dataclass(frozen=True, slots=True)
class SearchResult:
    """Represents the outcome of a knowledge store search."""

    note: Note
    score: int
    matched_terms: tuple[str, ...]
    snippet: str


class KnowledgeStore:
    """In-memory index for quick keyword searches across notes."""

    def __init__(self, notes: Sequence[Note]):
        """Build a store from ``notes`` and create a token lookup index."""

        self._notes: tuple[Note, ...] = tuple(notes)
        self._index: dict[str, set[int]] = {}
        for index, note in enumerate(self._notes):
            for token in note.iter_tokens():
                bucket = self._index.setdefault(token, set())
                bucket.add(index)

    @classmethod
    def from_paths(cls, paths: Iterable[Path | str]) -> KnowledgeStore:
        """Create a knowledge store from iterable ``paths``."""

        notes = list(load_notes_from_paths(paths))
        return cls(notes)

    @property
    def notes(self) -> tuple[Note, ...]:
        """Return all notes tracked by the store."""

        return self._notes

    def search(
        self,
        query: str,
        *,
        required_tags: Sequence[str] | None = None,
        limit: int | None = None,
    ) -> list[SearchResult]:
        """Return ranked search results for ``query``."""

        tokens = _tokenize(query)
        if not tokens:
            raise ValueError("query must include at least one searchable term")

        scores: dict[int, int] = {}
        matched_terms: dict[int, set[str]] = {}
        for token in tokens:
            for note_index in self._index.get(token, ()):  # pragma: no branch - simple lookup
                scores[note_index] = scores.get(note_index, 0) + 1
                matched_terms.setdefault(note_index, set()).add(token)

        if not scores:
            return []

        filtered_tags = tuple(required_tags or ())
        results: list[SearchResult] = []
        for note_index, score in scores.items():
            note = self._notes[note_index]
            if not note.matches_tags(filtered_tags):
                continue
            terms = tuple(sorted(matched_terms.get(note_index, set())))
            snippet = _build_snippet(note, terms)
            results.append(
                SearchResult(note=note, score=score, matched_terms=terms, snippet=snippet)
            )

        results.sort(
            key=lambda result: (-result.score, result.note.title.lower(), result.note.identifier)
        )
        if limit is not None:
            return results[: max(limit, 0)]
        return results


def load_notes_from_paths(paths: Iterable[Path | str]) -> Iterator[Note]:
    """Yield :class:`Note` objects derived from ``paths``."""

    for raw_path in paths:
        path = Path(raw_path)
        if not path.exists() or path.is_dir():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        metadata, body = _split_front_matter(text)
        tags = _extract_tags(metadata)
        title = metadata.get("title") or _derive_title(body, fallback=path.stem)
        identifier = str(path)
        yield Note(
            identifier=identifier,
            title=title,
            content=body,
            tags=tuple(tags),
            path=path,
        )


def _tokenize(text: str) -> list[str]:
    return [match.group(0).lower() for match in _WORD_PATTERN.finditer(text)]


def _split_front_matter(text: str) -> tuple[dict[str, str], str]:
    lines = text.splitlines()
    if len(lines) >= 2 and lines[0].strip() == "---":
        metadata: dict[str, str] = {}
        collected: list[str] = []
        i = 1
        while i < len(lines):
            line = lines[i].strip()
            if line == "---" or line == "...":
                break
            collected.append(lines[i])
            i += 1
        else:
            return {}, text
        raw = "\n".join(collected)
        metadata = _parse_simple_front_matter(raw)
        start = i + 1
        body = "\n".join(lines[start:]).lstrip("\n")
        return metadata, body
    return {}, text


def _parse_simple_front_matter(block: str) -> dict[str, str]:
    metadata: dict[str, str] = {}
    current_key: str | None = None
    collected_list: list[str] = []
    for line in block.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("-") and current_key:
            collected_list.append(stripped.lstrip("- "))
            continue
        if ":" in stripped:
            if current_key and collected_list:
                metadata[current_key] = ", ".join(collected_list)
                collected_list = []
            key, _, value = stripped.partition(":")
            key = key.strip().lower()
            value = value.strip()
            if value:
                metadata[key] = _normalize_value(value)
                current_key = None
            else:
                current_key = key
            continue
        if current_key:  # pragma: no branch - simple append covered by preceding tests
            collected_list.append(stripped)
    if current_key and collected_list:
        metadata[current_key] = ", ".join(collected_list)
    return metadata


def _normalize_value(value: str) -> str:
    value = value.strip().strip("[]")
    if not value:
        return ""
    if "," in value:
        parts = [segment.strip() for segment in value.split(",") if segment.strip()]
        return ", ".join(parts)
    return value


def _extract_tags(metadata: dict[str, str]) -> tuple[str, ...]:
    raw = metadata.get("tags")
    if not raw:
        return ()
    parts = [segment.strip() for segment in raw.replace(";", ",").split(",") if segment.strip()]
    normalized = tuple(dict.fromkeys(part.lower() for part in parts))
    return normalized


def _derive_title(content: str, *, fallback: str) -> str:
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("# ") or fallback
        if stripped:
            return stripped
    return fallback


def _build_snippet(note: Note, terms: Sequence[str]) -> str:
    if not note.content:
        return ""
    lower_content = note.content.lower()
    for term in terms:
        index = lower_content.find(term)
        if index != -1:
            start = max(0, index - 40)
            end = min(len(note.content), index + len(term) + 40)
            snippet = note.content[start:end].replace("\n", " ").strip()
            if start > 0:
                snippet = "..." + snippet
            if end < len(note.content):
                snippet += "..."
            return snippet
    preview = note.content[:80].replace("\n", " ").strip()
    if len(note.content) > 80:
        preview += "..."
    return preview


__all__ = [
    "KnowledgeStore",
    "Note",
    "SearchResult",
    "load_notes_from_paths",
]
