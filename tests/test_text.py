"""Tests for :mod:`gabriel.text`."""

from __future__ import annotations

from pathlib import Path

import pytest

from gabriel.text import (
    _character_name,
    find_hidden_characters,
    format_findings,
    main,
    normalize_allow_value,
    scan_paths,
)

ZWSP = chr(0x200B)
ZWJ = chr(0x200D)
RLM = chr(0x200F)
WORD_JOINER = chr(0x2060)


def test_find_hidden_characters_detects_zero_width_space() -> None:
    findings = find_hidden_characters(f"hello{ZWSP}world")
    assert len(findings) == 1  # nosec B101
    finding = findings[0]
    assert finding.character == ZWSP  # nosec B101
    assert finding.line == 1  # nosec B101
    assert finding.column == 6  # nosec B101
    assert finding.index == 5  # nosec B101


def test_find_hidden_characters_tracks_line_numbers() -> None:
    findings = find_hidden_characters(f"line1\nline{ZWJ}2")
    assert [(f.line, f.column) for f in findings] == [(2, 5)]  # nosec B101


def test_scan_paths_groups_findings(tmp_path: Path) -> None:
    file_path = tmp_path / "example.txt"
    file_path.write_text(f"safe{ZWSP}text")
    grouped = scan_paths([file_path])
    assert file_path in grouped  # nosec B101
    assert grouped[file_path][0].path == file_path  # nosec B101


def test_format_findings_creates_report(tmp_path: Path) -> None:
    file_path = tmp_path / "report.txt"
    file_path.write_text(f"safe{RLM}text")
    findings = scan_paths([file_path])
    report = format_findings(findings)
    assert "report.txt" in report  # nosec B101
    assert "U+200F" in report  # nosec B101


def test_main_reports_findings(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    file_path = tmp_path / "hidden.txt"
    file_path.write_text(f"value{WORD_JOINER}")
    exit_code = main([str(file_path)])
    captured = capsys.readouterr()
    assert exit_code == 1  # nosec B101
    assert "U+2060" in captured.err  # nosec B101
    assert "hidden.txt" in captured.err  # nosec B101


def test_main_respects_allow_list(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    file_path = tmp_path / "allowed.txt"
    file_path.write_text(f"value{ZWSP}")
    exit_code = main(["--allow", "U+200B", str(file_path)])
    captured = capsys.readouterr()
    assert exit_code == 0  # nosec B101
    assert captured.err == ""  # nosec B101


def test_normalize_allow_value_rejects_empty() -> None:
    with pytest.raises(ValueError):
        normalize_allow_value("   ")


def test_normalize_allow_value_unknown_name() -> None:
    with pytest.raises(ValueError):
        normalize_allow_value("NOT A NAME")


def test_character_name_uses_unicodedata() -> None:
    assert _character_name("A") == "LATIN CAPITAL LETTER A"  # nosec B101


def test_iter_hidden_characters_handles_carriage_return() -> None:
    findings = find_hidden_characters(f"line1\rline{ZWSP}")
    assert len(findings) == 1  # nosec B101
    assert findings[0].line == 2  # nosec B101


def test_scan_path_handles_decode_errors(tmp_path: Path) -> None:
    file_path = tmp_path / "mixed.txt"
    data = f"value{ZWSP}".encode("utf-8") + b"\xff"
    file_path.write_bytes(data)
    findings = scan_paths([file_path])[file_path]
    assert findings[0].character == ZWSP  # nosec B101


def test_scan_paths_skips_missing_targets(tmp_path: Path) -> None:
    missing = tmp_path / "missing.txt"
    assert scan_paths([missing]) == {}  # nosec B101


def test_main_returns_zero_without_paths() -> None:
    assert main([]) == 0  # nosec B101


def test_main_errors_on_invalid_allow(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        main(["--allow", "U+XYZ", "README.md"])
    captured = capsys.readouterr()
    assert "invalid literal" in captured.err  # nosec B101


__all__: list[str] = []
