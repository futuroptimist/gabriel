"""Tests for :mod:`gabriel.text`."""

from __future__ import annotations

from pathlib import Path

import pytest

from gabriel.text import (
    _character_name,
    _HTMLTextExtractor,
    find_hidden_characters,
    format_findings,
    main,
    normalize_allow_value,
    sanitize_prompt,
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
    data = f"value{ZWSP}".encode() + b"\xff"
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


def test_sanitize_prompt_strips_zero_width_and_markdown_images() -> None:
    payload = f"Click here{ZWSP}!<br/>![payload](https://evil.test/payload.png)"
    sanitized = sanitize_prompt(payload)
    assert ZWSP not in sanitized  # nosec B101
    assert "payload" not in sanitized  # nosec B101
    assert "https://evil.test" not in sanitized  # nosec B101
    assert sanitized == "Click here!"  # nosec B101


def test_sanitize_prompt_removes_html_and_script_blocks() -> None:
    html = "<p>Hello <strong>World</strong></p><script>alert('x')</script><div>Stay safe</div>"
    sanitized = sanitize_prompt(html)
    lines = sanitized.splitlines()
    assert "<" not in sanitized  # nosec B101
    assert "alert" not in sanitized  # nosec B101
    assert "Hello World" in lines[0]  # nosec B101
    assert any("Stay safe" in line for line in lines)  # nosec B101


def test_sanitize_prompt_drops_reference_style_images() -> None:
    text = "![diagram][diagram]\n\n[diagram]: https://example.com/assets/diagram.svg"
    sanitized = sanitize_prompt(text)
    assert sanitized == ""  # nosec B101


def test_sanitize_prompt_removes_angle_bracket_references() -> None:
    text = "![chart][chart]\n\n[chart]: <https://attacker.test/chart.png>"
    sanitized = sanitize_prompt(text)
    assert sanitized == ""  # nosec B101


def test_sanitize_prompt_removes_data_uri_references() -> None:
    text = (
        "Look! ![sneaky][sneaky]\n\n" "[sneaky]: data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA"
    )
    sanitized = sanitize_prompt(text)
    assert sanitized == "Look!"  # nosec B101


def test_sanitize_prompt_preserves_non_image_reference() -> None:
    text = "Reference [guide][guide]\n\n" "[guide]: https://example.com/docs/security-checklist"
    sanitized = sanitize_prompt(text)
    assert "https://example.com/docs/security-checklist" in sanitized  # nosec B101


def test_sanitize_prompt_decodes_html_entities() -> None:
    text = "<p>Keep &amp; cherish &#169; notes</p>"
    sanitized = sanitize_prompt(text)
    assert sanitized == "Keep & cherish © notes"  # nosec B101


def test_sanitize_prompt_discards_script_payloads() -> None:
    text = "<script>ignore &amp; &#169; <br/></script><p>Visible</p>"
    sanitized = sanitize_prompt(text)
    assert sanitized == "Visible"  # nosec B101


def test_html_text_extractor_suppresses_entities_inside_blocks() -> None:
    parser = _HTMLTextExtractor()
    parser.handle_starttag("script", [])
    parser.handle_entityref("amp")
    parser.handle_charref("169")
    parser.handle_startendtag("br", [])
    parser.handle_endtag("script")
    assert parser.get_text() == ""  # nosec B101


__all__: list[str] = []
