"""Utilities for detecting zero-width or hidden Unicode characters."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys
import unicodedata
from typing import Iterable, Iterator, Sequence

_MONITORED_CHARACTERS: dict[str, str] = {
    "\u200b": "ZERO WIDTH SPACE",
    "\u200c": "ZERO WIDTH NON-JOINER",
    "\u200d": "ZERO WIDTH JOINER",
    "\u200e": "LEFT-TO-RIGHT MARK",
    "\u200f": "RIGHT-TO-LEFT MARK",
    "\u202a": "LEFT-TO-RIGHT EMBEDDING",
    "\u202b": "RIGHT-TO-LEFT EMBEDDING",
    "\u202c": "POP DIRECTIONAL FORMATTING",
    "\u202d": "LEFT-TO-RIGHT OVERRIDE",
    "\u202e": "RIGHT-TO-LEFT OVERRIDE",
    "\u2060": "WORD JOINER",
    "\u2066": "LEFT-TO-RIGHT ISOLATE",
    "\u2067": "RIGHT-TO-LEFT ISOLATE",
    "\u2068": "FIRST STRONG ISOLATE",
    "\u2069": "POP DIRECTIONAL ISOLATE",
    "\ufeff": "ZERO WIDTH NO-BREAK SPACE",
}


@dataclass(frozen=True, slots=True)
class HiddenCharacter:
    """Details about a detected hidden character."""

    character: str
    name: str
    line: int
    column: int
    index: int
    path: Path | None = None

    @property
    def codepoint(self) -> str:
        """Return the Unicode codepoint for the character."""

        return f"U+{ord(self.character):04X}"


def _character_name(character: str) -> str:
    """Return a human-readable name for ``character``."""

    if character in _MONITORED_CHARACTERS:
        return _MONITORED_CHARACTERS[character]
    try:
        return unicodedata.name(character)
    except ValueError:  # pragma: no cover - highly unlikely for monitored characters
        return "UNKNOWN CHARACTER"


def normalize_allow_value(value: str) -> str:
    """Convert ``value`` into a literal character for allow-list comparisons."""

    stripped = value.strip()
    if not stripped:
        raise ValueError("Allow-list values cannot be empty")
    if stripped.startswith("U+") or stripped.startswith("u+"):
        return chr(int(stripped[2:], 16))
    if len(stripped) == 1:
        return stripped
    try:
        return unicodedata.lookup(stripped)
    except KeyError as exc:  # pragma: no cover - defensive guard
        raise ValueError(f"Unknown Unicode name: {stripped}") from exc


def iter_hidden_characters(
    text: str, *, allow: Iterable[str] | None = None
) -> Iterator[HiddenCharacter]:
    """Yield :class:`HiddenCharacter` items found in ``text``."""

    allow_set = {normalize_allow_value(value) for value in (allow or ())}

    line = 1
    column = 1
    for index, character in enumerate(text):
        if character in allow_set:
            pass
        elif character in _MONITORED_CHARACTERS:
            yield HiddenCharacter(
                character=character,
                name=_character_name(character),
                line=line,
                column=column,
                index=index,
            )
        if character == "\n":
            line += 1
            column = 1
        elif character == "\r":
            line += 1
            column = 1
        else:
            column += 1


def find_hidden_characters(text: str, *, allow: Iterable[str] | None = None) -> list[HiddenCharacter]:
    """Return a list of :class:`HiddenCharacter` items present in ``text``."""

    return list(iter_hidden_characters(text, allow=allow))


def scan_path(path: Path, *, allow: Iterable[str] | None = None) -> list[HiddenCharacter]:
    """Scan a single file ``path`` for hidden characters."""

    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8", errors="ignore")
    results = [
        HiddenCharacter(
            character=finding.character,
            name=finding.name,
            line=finding.line,
            column=finding.column,
            index=finding.index,
            path=path,
        )
        for finding in iter_hidden_characters(text, allow=allow)
    ]
    return results


def scan_paths(
    paths: Iterable[Path], *, allow: Iterable[str] | None = None
) -> dict[Path, list[HiddenCharacter]]:
    """Scan ``paths`` and return findings grouped by file path."""

    grouped: dict[Path, list[HiddenCharacter]] = {}
    for raw_path in paths:
        path = Path(raw_path)
        if not path.exists() or path.is_dir():
            continue
        findings = scan_path(path, allow=allow)
        if findings:
            grouped[path] = findings
    return grouped


def format_findings(findings: dict[Path, list[HiddenCharacter]]) -> str:
    """Create a human-readable report for ``findings``."""

    lines: list[str] = []
    for path in sorted(findings):
        for finding in findings[path]:
            lines.append(
                f"{path}:{finding.line}:{finding.column}: {finding.codepoint} {finding.name}"
            )
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for ``python -m gabriel.text``."""

    parser = argparse.ArgumentParser(description="Detect hidden zero-width characters")
    parser.add_argument("paths", nargs="*", help="Files to scan for hidden characters")
    parser.add_argument(
        "--allow",
        action="append",
        default=[],
        help="Unicode codepoint (e.g. U+200B) or name to allow",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    if not args.paths:
        return 0

    try:
        allow_values = [normalize_allow_value(value) for value in args.allow]
    except ValueError as error:
        parser.error(str(error))
        return 2  # pragma: no cover - argparse.error exits before reaching here

    findings = scan_paths((Path(path) for path in args.paths), allow=allow_values)
    if not findings:
        return 0

    report = format_findings(findings)
    print(report, file=sys.stderr)
    return 1


if __name__ == "__main__":  # pragma: no cover - exercised via CLI
    raise SystemExit(main())
