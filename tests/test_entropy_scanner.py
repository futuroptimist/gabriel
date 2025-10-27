"""Tests for the entropy-based secret scanner."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from gabriel import (
    EntropyFinding,
    EntropyScanner,
    EntropyScannerConfig,
    scan_paths_for_entropy,
)
from gabriel.security.entropy import _shannon_entropy


def test_scan_text_flags_high_entropy_base64() -> None:
    scanner = EntropyScanner()
    payload = "token=ZXhhbXBsZV9zZWNyZXRfdmFsdWU="

    findings = scanner.scan_text(payload)

    assert len(findings) == 1
    finding = findings[0]
    assert isinstance(finding, EntropyFinding)
    assert finding.line_number == 1
    assert finding.pattern == "base64"
    assert finding.secret == "ZXhhbXBsZV9zZWNyZXRfdmFsdWU="
    assert finding.entropy >= scanner.config.min_entropy
    assert finding.as_dict()["secret"] == finding.secret
    assert "path" not in finding.as_dict()


def test_allowlist_patterns_suppress_findings() -> None:
    allow = re.compile(r"ZXhhbXBsZV9zZWNyZXRfdmFsdWU=")
    scanner = EntropyScanner(EntropyScannerConfig(allowlist=(allow,)))

    assert scanner.scan_text("ZXhhbXBsZV9zZWNyZXRfdmFsdWU=") == []


def test_allowlist_strings_suppress_findings() -> None:
    scanner = EntropyScanner(EntropyScannerConfig(allowlist=("ZXhhbXBsZV9zZWNyZXRfdmFsdWU=",)))

    assert scanner.scan_text("ZXhhbXBsZV9zZWNyZXRfdmFsdWU=") == []


def test_scan_paths_skips_binary_and_large_files(tmp_path: Path) -> None:
    secret = "ZXhhbXBsZV9zZWNyZXRfdmFsdWU="
    text_file = tmp_path / "secrets.txt"
    text_file.write_text(f"token={secret}\n", encoding="utf-8")

    binary_file = tmp_path / "artifact.bin"
    binary_file.write_bytes(b"\x00\x01\x02")

    oversized = tmp_path / "huge.txt"
    oversized.write_text(secret, encoding="utf-8")

    config = EntropyScannerConfig(max_file_bytes=5)
    scanner = EntropyScanner(config)

    findings = scanner.scan_paths([text_file, binary_file, oversized])

    assert len(findings) == 0

    findings = scan_paths_for_entropy([text_file])

    assert len(findings) == 1
    finding = findings[0]
    payload = finding.as_dict()
    assert payload["path"] == str(text_file)
    assert finding.line_number == 1


def test_min_length_and_entropy_controls(tmp_path: Path) -> None:
    noise = "A" * 40
    file_path = tmp_path / "noise.txt"
    file_path.write_text(noise, encoding="utf-8")

    scanner = EntropyScanner(EntropyScannerConfig(min_length=10, min_entropy=3.0))

    assert scanner.scan_paths([file_path]) == []

    relaxed = EntropyScanner(EntropyScannerConfig(min_length=4, min_entropy=0.5))
    assert relaxed.scan_text("A" * 8) == []


def test_configuration_validation() -> None:
    with pytest.raises(ValueError):
        EntropyScannerConfig(min_length=0)

    with pytest.raises(ValueError):
        EntropyScannerConfig(min_entropy=0.0)

    with pytest.raises(ValueError):
        EntropyScannerConfig(max_file_bytes=0)

    with pytest.raises(TypeError):
        EntropyScannerConfig(allowlist=(object(),))

    with pytest.raises(ValueError):
        EntropyScannerConfig(patterns={})

    with pytest.raises(TypeError):
        EntropyScannerConfig(patterns={"bad": "[A-Z]+"})


def test_shannon_entropy_handles_empty_input() -> None:
    assert _shannon_entropy("") == 0.0


def test_directory_and_missing_paths_are_ignored(tmp_path: Path) -> None:
    missing = tmp_path / "missing.txt"
    scanner = EntropyScanner()

    assert scanner.scan_paths([tmp_path, missing]) == []


def test_scan_paths_handles_stat_errors(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    secret = tmp_path / "secret.txt"
    secret.write_text("ZXhhbXBsZV9zZWNyZXRfdmFsdWU=", encoding="utf-8")

    original_stat = Path.stat
    original_is_file = Path.is_file

    def fake_stat(self: Path, *args: object, **kwargs: object) -> object:
        if self == secret:
            raise OSError("boom")
        return original_stat(self, *args, **kwargs)

    def fake_is_file(self: Path) -> bool:
        if self == secret:
            return True
        return original_is_file(self)

    monkeypatch.setattr(Path, "stat", fake_stat)
    monkeypatch.setattr(Path, "is_file", fake_is_file)
    scanner = EntropyScanner()

    assert scanner._scan_file(secret) == []


def test_scan_paths_handles_binary_open_errors(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    secret = tmp_path / "secret.txt"
    secret.write_text("ZXhhbXBsZV9zZWNyZXRfdmFsdWU=", encoding="utf-8")

    original_open = Path.open

    def fake_open(self: Path, mode: str = "r", *args: object, **kwargs: object):
        if self == secret and "b" in mode:
            raise OSError("binary fail")
        return original_open(self, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "open", fake_open)
    scanner = EntropyScanner()

    assert scanner.scan_paths([secret]) == []


def test_scan_paths_handles_text_open_errors(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    secret = tmp_path / "secret.txt"
    secret.write_text("ZXhhbXBsZV9zZWNyZXRfdmFsdWU=", encoding="utf-8")

    original_open = Path.open

    def fake_open(self: Path, mode: str = "r", *args: object, **kwargs: object):
        if self == secret and "b" not in mode:
            raise OSError("text fail")
        return original_open(self, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "open", fake_open)
    scanner = EntropyScanner()

    assert scanner.scan_paths([secret]) == []


def test_custom_patterns_respect_min_length() -> None:
    short_pattern = re.compile(r"[A-Za-z0-9]{4,}")
    config = EntropyScannerConfig(min_length=10, min_entropy=0.1, patterns={"short": short_pattern})
    scanner = EntropyScanner(config)

    assert scanner.scan_text("abcd") == []
