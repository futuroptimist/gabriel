"""Prompt-injection linter for Markdown content."""

from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

Severity = Literal["warning", "error"]


@dataclass(frozen=True, slots=True)
class PromptLintRule:
    """Represents a single heuristic used to detect risky prompt instructions."""

    name: str
    pattern: re.Pattern[str]
    message: str
    severity: Severity = "error"


@dataclass(frozen=True, slots=True)
class PromptLintFinding:
    """A lint finding surfaced by :mod:`gabriel.prompt_lint`."""

    rule: PromptLintRule
    line: int
    column: int
    snippet: str
    path: Path | None = None

    @property
    def rule_name(self) -> str:
        """Return the machine-friendly rule identifier."""
        return self.rule.name

    @property
    def severity(self) -> Severity:
        """Expose the severity of the triggering rule."""
        return self.rule.severity

    @property
    def message(self) -> str:
        """Return the human-readable lint message."""
        return self.rule.message


_DEFAULT_RULES: tuple[PromptLintRule, ...] = (
    PromptLintRule(
        name="ignore-previous-instructions",
        pattern=re.compile(
            r"(?i)\b(?:ignore|forget)\b[\s\S]{0,40}"
            r"\b(?:previous|prior|above)\b[\s\S]{0,40}"
            r"\b(?:instructions?|messages?|prompts?)\b"
        ),
        message="Text instructs the reader to ignore previous guidance, a common injection tactic.",
    ),
    PromptLintRule(
        name="disable-guardrails",
        pattern=re.compile(
            r"(?i)\b(?:disable|bypass|remove)\b[\s\S]{0,40}"
            r"\b(?:safety|guardrail|security)\b[\s\S]{0,40}"
            r"\b(?:checks|systems|controls|filters)\b"
        ),
        message="Detected language attempting to disable safety guardrails.",
    ),
    PromptLintRule(
        name="system-prompt-overrides",
        pattern=re.compile(
            r"(?i)\byou\b[\s\S]{0,40}\bare\b[\s\S]{0,40}\bno\b[\s\S]{0,40}"
            r"\blonger\b[\s\S]{0,40}\bbound\b"
        ),
        message="Phrase attempts to override system prompt constraints.",
    ),
    PromptLintRule(
        name="remote-markdown-images",
        pattern=re.compile(
            r"""
            !\[[^\]]*\]\(      # image link open
                \s*
                (?:
                    <\s*(?:https?|data):[^>]+?\s*>  # angle-bracketed target
                    |
                    (?:https?|data):[^)]+?           # bare target
                )
                \s*
            \)
            """,
            re.IGNORECASE | re.VERBOSE,
        ),
        message="Remote or data URI Markdown images can smuggle hostile instructions.",
        severity="warning",
    ),
    PromptLintRule(
        name="inline-script-tag",
        pattern=re.compile(r"<script\b", re.IGNORECASE),
        message="Inline <script> tags are disallowed in trusted Markdown.",
    ),
    PromptLintRule(
        name="inline-iframe",
        pattern=re.compile(r"<iframe\b", re.IGNORECASE),
        message="Inline <iframe> tags can exfiltrate data in rendered docs.",
    ),
)

_DISABLE_DIRECTIVE = re.compile(
    r"<!--\s*gabriel-prompt-lint:\s*disable\s*=\s*([a-z0-9_,\-\s]+)\s*-->",
    re.IGNORECASE,
)


def _find_disabled_rules(text: str) -> set[str]:
    disabled: set[str] = set()
    for match in _DISABLE_DIRECTIVE.finditer(text):
        tokens = match.group(1).split(",")
        for token in tokens:
            normalized = token.strip().lower()
            if normalized:
                disabled.add(normalized)
    return disabled


def _offset_to_position(text: str, offset: int) -> tuple[int, int]:
    line = text.count("\n", 0, offset) + 1
    last_newline = text.rfind("\n", 0, offset)
    if last_newline == -1:
        column = offset + 1
    else:
        column = offset - last_newline
    return line, column


def lint_text(
    text: str,
    *,
    rules: Iterable[PromptLintRule] | None = None,
    disabled_rules: Iterable[str] | None = None,
    path: Path | None = None,
) -> list[PromptLintFinding]:
    """Return lint findings for ``text`` using the configured ``rules``."""
    active_rules = tuple(rules or _DEFAULT_RULES)
    disabled_from_text = _find_disabled_rules(text)
    disabled_from_cli = {rule.lower() for rule in (disabled_rules or [])}
    disabled = {"all"} if "all" in disabled_from_text or "all" in disabled_from_cli else set()
    if not disabled:
        disabled = disabled_from_text | disabled_from_cli
    findings: list[PromptLintFinding] = []

    for rule in active_rules:
        if disabled and ("all" in disabled or rule.name.lower() in disabled):
            continue
        for match in rule.pattern.finditer(text):
            start = match.start()
            line, column = _offset_to_position(text, start)
            snippet = match.group(0).strip()
            findings.append(
                PromptLintFinding(
                    rule=rule,
                    line=line,
                    column=column,
                    snippet=snippet,
                    path=path,
                )
            )
    return findings


def lint_path(
    path: Path,
    *,
    rules: Iterable[PromptLintRule] | None = None,
    disabled_rules: Iterable[str] | None = None,
) -> list[PromptLintFinding]:
    """Load ``path`` and return prompt-injection lint findings."""
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8", errors="ignore")
    findings = lint_text(text, rules=rules, disabled_rules=disabled_rules, path=path)
    return findings


def lint_paths(
    paths: Iterable[Path],
    *,
    rules: Iterable[PromptLintRule] | None = None,
    disabled_rules: Iterable[str] | None = None,
) -> dict[Path, list[PromptLintFinding]]:
    """Return prompt-injection findings grouped by file path."""
    grouped: dict[Path, list[PromptLintFinding]] = {}
    for raw_path in paths:
        path = Path(raw_path)
        if not path.exists() or path.is_dir():
            continue
        findings = lint_path(path, rules=rules, disabled_rules=disabled_rules)
        if findings:
            grouped[path] = findings
    return grouped


def format_findings(findings: dict[Path, list[PromptLintFinding]]) -> str:
    """Return a human-readable summary for ``findings``."""
    lines: list[str] = []
    for path in sorted(findings):
        for finding in findings[path]:
            message = (
                f"{path}:{finding.line}:{finding.column}: "
                f"{finding.rule_name} ({finding.severity}) — {finding.message}"
            )
            lines.append(message)
    return "\n".join(lines)


def iter_paths_from_cli(paths: Sequence[str]) -> Iterator[Path]:
    """Yield :class:`Path` objects for CLI arguments."""
    for raw in paths:
        yield Path(raw)


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for ``python -m gabriel.prompt_lint``."""
    parser = argparse.ArgumentParser(description="Lint Markdown for prompt-injection red flags")
    parser.add_argument("paths", nargs="*", help="Markdown files to scan")
    parser.add_argument(
        "--disable",
        action="append",
        default=[],
        help="Comma-separated rule names to disable (e.g. ignore-previous-instructions)",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    if not args.paths:
        return 0

    disabled: list[str] = []
    for value in args.disable:
        disabled.extend(item.strip() for item in value.split(","))

    findings = lint_paths(iter_paths_from_cli(args.paths), disabled_rules=disabled)
    if not findings:
        return 0

    report = format_findings(findings)
    print(report, file=sys.stderr)
    return 1


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
