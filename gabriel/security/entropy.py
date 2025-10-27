"""High-entropy secret scanning helpers for Gabriel agents."""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Iterator, Mapping, MutableMapping, Sequence


Pattern = re.Pattern[str]


def _build_default_patterns(min_length: int) -> dict[str, Pattern]:
    """Return regex patterns that identify high-entropy token candidates."""

    base64_core = rf"[A-Za-z0-9+/]{{{min_length},}}"
    base64_pattern = (
        rf"(?<![A-Za-z0-9+/]){base64_core}(?:=){{0,2}}(?![A-Za-z0-9+/=])"
    )
    hex_pattern = rf"(?<![0-9A-Fa-f])[0-9A-Fa-f]{{{min_length},}}(?![0-9A-Fa-f])"
    generic_pattern = rf"(?<![A-Za-z0-9])[-_A-Za-z0-9]{{{min_length},}}(?![A-Za-z0-9])"

    return {
        "base64": re.compile(base64_pattern),
        "hex": re.compile(hex_pattern),
        "generic": re.compile(generic_pattern),
    }


def _shannon_entropy(value: str) -> float:
    if not value:
        return 0.0

    counts = Counter(value)
    length = len(value)
    entropy = 0.0
    for count in counts.values():
        probability = count / length
        entropy -= probability * math.log2(probability)
    return entropy


@dataclass(frozen=True, slots=True)
class EntropyFinding:
    """Represents a potential secret discovered during an entropy scan."""

    path: Path | None
    line_number: int
    secret: str
    entropy: float
    pattern: str

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-serialisable representation of the finding."""

        payload: dict[str, object] = {
            "line": self.line_number,
            "secret": self.secret,
            "entropy": round(self.entropy, 4),
            "pattern": self.pattern,
        }
        if self.path is not None:
            payload["path"] = str(self.path)
        return payload


@dataclass(slots=True)
class EntropyScannerConfig:
    """Configuration options for :class:`EntropyScanner`."""

    min_length: int = 20
    min_entropy: float = 4.0
    patterns: Mapping[str, Pattern] | None = None
    allowlist: Sequence[str | Pattern] = ()
    max_file_bytes: int | None = 1_000_000

    compiled_patterns: MutableMapping[str, Pattern] = field(init=False)
    _allowlist_strings: set[str] = field(init=False)
    _allowlist_patterns: tuple[Pattern, ...] = field(init=False)

    def __post_init__(self) -> None:
        if self.min_length <= 0:
            msg = "min_length must be a positive integer"
            raise ValueError(msg)
        if self.min_entropy <= 0:
            msg = "min_entropy must be a positive floating point value"
            raise ValueError(msg)
        if self.max_file_bytes is not None and self.max_file_bytes <= 0:
            msg = "max_file_bytes must be positive when provided"
            raise ValueError(msg)

        supplied_patterns = self.patterns
        if supplied_patterns is None:
            compiled = _build_default_patterns(self.min_length)
        else:
            compiled = {name: pattern for name, pattern in supplied_patterns.items()}
            if not compiled:
                msg = "patterns must not be empty"
                raise ValueError(msg)
        for name, pattern in compiled.items():
            if not isinstance(pattern, re.Pattern):
                msg = f"Pattern for '{name}' is not a compiled regular expression"
                raise TypeError(msg)

        self.compiled_patterns = compiled
        strings: set[str] = set()
        regexes: list[Pattern] = []
        for entry in self.allowlist:
            if isinstance(entry, str):
                strings.add(entry)
            elif isinstance(entry, re.Pattern):
                regexes.append(entry)
            else:
                msg = "allowlist entries must be strings or compiled regex patterns"
                raise TypeError(msg)
        self._allowlist_strings = strings
        self._allowlist_patterns = tuple(regexes)


class EntropyScanner:
    """Detects high-entropy tokens in text buffers or filesystem paths."""

    def __init__(self, config: EntropyScannerConfig | None = None) -> None:
        self.config = config or EntropyScannerConfig()

    def scan_text(self, text: str, *, path: str | Path | None = None) -> list[EntropyFinding]:
        """Scan the provided text for suspicious high-entropy strings."""

        resolved_path = Path(path) if isinstance(path, (str, Path)) else None
        lines = text.splitlines()
        return list(self._scan_lines(lines, resolved_path))

    def scan_paths(self, paths: Iterable[str | Path]) -> list[EntropyFinding]:
        """Scan filesystem paths for high-entropy tokens."""

        findings: list[EntropyFinding] = []
        for raw in paths:
            candidate = Path(raw)
            if candidate.is_dir():
                continue
            findings.extend(self._scan_file(candidate))
        return findings

    def _scan_file(self, path: Path) -> list[EntropyFinding]:
        if not path.is_file():
            return []
        try:
            if self.config.max_file_bytes is not None and path.stat().st_size > self.config.max_file_bytes:
                return []
        except OSError:
            return []

        try:
            with path.open("rb") as handle:
                sample = handle.read(1024)
        except OSError:
            return []

        if b"\0" in sample:
            return []

        try:
            with path.open("r", encoding="utf-8", errors="ignore") as handle:
                return list(self._scan_lines(handle, path))
        except OSError:
            return []

    def _scan_lines(self, lines: Iterable[str], path: Path | None) -> Iterator[EntropyFinding]:
        for line_number, line in enumerate(lines, start=1):
            spans_seen: set[tuple[int, int]] = set()
            for name, pattern in self.config.compiled_patterns.items():
                for match in pattern.finditer(line):
                    span = match.span()
                    if span in spans_seen:
                        continue
                    spans_seen.add(span)

                    secret = match.group(0)
                    if len(secret) < self.config.min_length:
                        continue
                    if self._is_allowlisted(secret):
                        continue

                    entropy = _shannon_entropy(secret)
                    if entropy < self.config.min_entropy:
                        continue

                    yield EntropyFinding(
                        path=path,
                        line_number=line_number,
                        secret=secret,
                        entropy=entropy,
                        pattern=name,
                    )

    def _is_allowlisted(self, token: str) -> bool:
        if token in self.config._allowlist_strings:
            return True
        return any(pattern.search(token) for pattern in self.config._allowlist_patterns)


def scan_paths_for_entropy(
    paths: Iterable[str | Path], *, config: EntropyScannerConfig | None = None
) -> list[EntropyFinding]:
    """Convenience wrapper to scan filesystem paths using :class:`EntropyScanner`."""

    scanner = EntropyScanner(config=config)
    return scanner.scan_paths(paths)


__all__ = [
    "EntropyFinding",
    "EntropyScanner",
    "EntropyScannerConfig",
    "scan_paths_for_entropy",
]
