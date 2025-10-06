"""Utilities for building and searching a local security note index."""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path

_NOTE_PATTERNS = ("*.md", "*.txt", "*.rst")

_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9']+")
_PRINTABLE_BYTE_VALUES = frozenset({7, 8, 9, 10, 12, 13, *range(32, 127)})


@dataclass
class NoteDocument:
    """A plain-text note stored on disk."""

    path: Path
    title: str
    content: str

    @classmethod
    def from_bytes(
        cls,
        path: Path,
        data: bytes,
        *,
        encoding: str = "utf-8",
    ) -> NoteDocument:
        """Create a document from raw ``data``."""

        text = data.decode(encoding, errors="replace")
        lines = text.splitlines()
        first_line = lines[0].strip() if lines else ""
        title = first_line or path.stem
        return cls(path=path, title=title, content=text)

    @classmethod
    def from_path(
        cls,
        path: Path,
        *,
        encoding: str = "utf-8",
        max_bytes: int = 262_144,
    ) -> NoteDocument:
        """Load a note from ``path``.

        Parameters
        ----------
        path:
            The file to read.
        encoding:
            Preferred text encoding. Invalid sequences are replaced so ``UnicodeError`` is not
            raised.
        max_bytes:
            Limit read size in bytes to prevent unexpectedly huge documents from exhausting
            memory.
        """

        with path.open("rb") as buffer:
            data = buffer.read(max_bytes + 1)
        if len(data) > max_bytes:
            data = data[:max_bytes]
        return cls.from_bytes(path, data, encoding=encoding)


@dataclass(order=True)
class NoteMatch:
    """Search result pairing a note with its relevance score."""

    score: float
    document: NoteDocument = field(compare=False)

    def __post_init__(self) -> None:
        """Normalize the ``score`` to ``float`` for consistent ordering."""

        # Ensure scores can be compared reliably even when ``float`` rounding kicks in.
        self.score = float(self.score)


class NoteIndex:
    """Lightweight inverted index for local security notes."""

    def __init__(self, documents: Iterable[NoteDocument]):
        """Build an index from ``documents`` and pre-compute their token counters."""

        self._documents: list[NoteDocument] = []
        self._token_counters: list[Counter[str]] = []
        for document in documents:
            tokens = Counter(_tokenize(document.content))
            self._documents.append(document)
            self._token_counters.append(tokens)

    @property
    def documents(self) -> Sequence[NoteDocument]:
        """Return an immutable view of indexed documents."""

        return tuple(self._documents)

    def search(self, query: str, *, limit: int = 5) -> list[NoteMatch]:
        """Search notes for ``query`` ordered by relevance.

        The scoring function rewards overlapping tokens, exact substring matches, and fuzzy title
        matches. Results with a zero score are omitted.
        """

        normalized_query = query.strip()
        if not normalized_query:
            msg = "Query must contain at least one non-whitespace character."
            raise ValueError(msg)

        lowercase_query = normalized_query.lower()
        query_tokens = Counter(_tokenize(normalized_query))
        results: list[NoteMatch] = []

        for document, token_counter in zip(self._documents, self._token_counters, strict=False):
            token_overlap = sum(
                min(token_counter[token], query_tokens[token]) for token in query_tokens
            )
            substring_bonus = 0.0
            title_lower = document.title.lower()
            content_lower = document.content.lower()
            if lowercase_query in title_lower:
                substring_bonus += 3.0
            if lowercase_query in content_lower:
                substring_bonus += 1.5
            fuzzy_bonus = SequenceMatcher(None, title_lower, lowercase_query).ratio()
            if token_overlap == 0 and substring_bonus == 0.0 and fuzzy_bonus < 0.35:
                continue
            score = token_overlap + substring_bonus + fuzzy_bonus
            results.append(NoteMatch(score=score, document=document))

        results.sort(reverse=True)
        if limit <= 0:
            return results
        return results[:limit]

    @classmethod
    def from_directory(
        cls,
        root: Path | str,
        *,
        patterns: Sequence[str] | None = None,
        encoding: str = "utf-8",
        max_bytes: int = 262_144,
    ) -> NoteIndex:
        """Build an index from files beneath ``root`` matching ``patterns``."""

        directory = Path(root)
        file_patterns = tuple(patterns or _NOTE_PATTERNS)
        documents = list(_load_documents(directory, file_patterns, encoding, max_bytes))
        return cls(documents)


def _load_documents(
    directory: Path,
    patterns: Sequence[str],
    encoding: str,
    max_bytes: int,
) -> Iterator[NoteDocument]:
    seen: set[Path] = set()
    for pattern in patterns:
        for path in sorted(directory.rglob(pattern)):
            if path in seen or not path.is_file():
                continue
            seen.add(path)
            try:
                with path.open("rb") as buffer:
                    data = buffer.read(max_bytes + 1)
            except OSError:
                continue
            if len(data) > max_bytes:
                data = data[:max_bytes]
            if not _is_probably_text(data):
                continue
            yield NoteDocument.from_bytes(path, data, encoding=encoding)


def _tokenize(text: str) -> list[str]:
    return [match.group(0).lower() for match in _TOKEN_PATTERN.finditer(text)]


def _is_probably_text(data: bytes) -> bool:
    if not data:
        return True
    if b"\x00" in data:
        return False
    printable = sum(byte in _PRINTABLE_BYTE_VALUES for byte in data)
    return printable / len(data) >= 0.85


def index_security_notes(
    root: Path | str,
    *,
    patterns: Sequence[str] | None = None,
    encoding: str = "utf-8",
    max_bytes: int = 262_144,
) -> NoteIndex:
    """Return a :class:`NoteIndex` built from ``root``."""

    return NoteIndex.from_directory(root, patterns=patterns, encoding=encoding, max_bytes=max_bytes)


__all__ = [
    "NoteDocument",
    "NoteIndex",
    "NoteMatch",
    "index_security_notes",
]
