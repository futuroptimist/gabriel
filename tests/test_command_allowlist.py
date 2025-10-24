"""Tests for the command allowlist registry and CLI enforcement."""

from __future__ import annotations

from pathlib import Path

import pytest

from gabriel.security.command_allowlist import (
    CommandAllowlist,
    CommandAllowlistError,
    CommandNotAllowedError,
    TaskRule,
    load_default_allowlist,
)


def test_default_allowlist_covers_cli_tasks() -> None:
    allowlist = load_default_allowlist()

    assert "arithmetic" in allowlist.tasks
    assert allowlist.is_allowed("arithmetic", "add")
    assert allowlist.is_allowed("arithmetic", "sqrt")
    assert allowlist.is_allowed("secrets", "secret.get")
    assert allowlist.is_allowed("viewer", "viewer.serve")
    assert allowlist.is_allowed("ingestion", "crawl")
    assert not allowlist.is_allowed("unknown", "crawl")
    assert allowlist.tools_for("unknown") == ()

    with pytest.raises(CommandNotAllowedError):
        allowlist.require_allowed("arithmetic", "rm -rf /")


def test_task_rule_validates_tool_entries() -> None:
    with pytest.raises(CommandAllowlistError):
        TaskRule(name="ops", tools=("",))

    with pytest.raises(CommandAllowlistError):
        TaskRule(name="ops", tools=("deploy", "deploy"))


def test_command_allowlist_from_mapping_validates_entries() -> None:
    allowlist = CommandAllowlist.from_mapping({"ops": ["deploy", "build*"]})
    assert allowlist.is_allowed("ops", "deploy")
    assert allowlist.is_allowed("ops", "build-service")
    with pytest.raises(CommandNotAllowedError):
        allowlist.require_allowed("missing", "deploy")
    assert allowlist.tools_for("ops") == ("deploy", "build*")

    with pytest.raises(CommandAllowlistError):
        CommandAllowlist.from_mapping({"bad": [""]})
    with pytest.raises(CommandAllowlistError):
        CommandAllowlist.from_mapping({123: ["tool"]})  # type: ignore[arg-type, dict-item]
    with pytest.raises(CommandAllowlistError):
        CommandAllowlist.from_mapping({"ops": None})  # type: ignore[arg-type, dict-item]
    with pytest.raises(CommandAllowlistError):
        CommandAllowlist.from_mapping({})


def test_command_allowlist_from_file_rejects_invalid_config(tmp_path: Path) -> None:
    path = tmp_path / "allowlist.yaml"
    path.write_text("tasks:\n  sample: []\n", encoding="utf-8")

    with pytest.raises(CommandAllowlistError):
        CommandAllowlist.from_file(path)


def test_command_allowlist_from_file_validates_structure(tmp_path: Path) -> None:
    missing_tasks = tmp_path / "missing.yaml"
    missing_tasks.write_text("{}\n", encoding="utf-8")
    with pytest.raises(CommandAllowlistError):
        CommandAllowlist.from_file(missing_tasks)

    wrong_root = tmp_path / "wrong_root.yaml"
    wrong_root.write_text("- not-a-mapping\n", encoding="utf-8")
    with pytest.raises(CommandAllowlistError):
        CommandAllowlist.from_file(wrong_root)

    non_mapping = tmp_path / "non_mapping.yaml"
    non_mapping.write_text("tasks: []\n", encoding="utf-8")
    with pytest.raises(CommandAllowlistError):
        CommandAllowlist.from_file(non_mapping)

    non_string_key = tmp_path / "non_string.yaml"
    non_string_key.write_text("tasks:\n  1: {tools: [cmd]}\n", encoding="utf-8")
    with pytest.raises(CommandAllowlistError):
        CommandAllowlist.from_file(non_string_key)

    bad_description = tmp_path / "bad_description.yaml"
    bad_description.write_text(
        "tasks:\n  sample:\n    description: [1]\n    tools:\n      - cmd\n",
        encoding="utf-8",
    )
    with pytest.raises(CommandAllowlistError):
        CommandAllowlist.from_file(bad_description)

    missing_tools = tmp_path / "missing_tools.yaml"
    missing_tools.write_text("tasks:\n  sample: {}\n", encoding="utf-8")
    with pytest.raises(CommandAllowlistError):
        CommandAllowlist.from_file(missing_tools)

    wrong_type_tools = tmp_path / "wrong_type.yaml"
    wrong_type_tools.write_text("tasks:\n  sample:\n    tools: cmd\n", encoding="utf-8")
    with pytest.raises(CommandAllowlistError):
        CommandAllowlist.from_file(wrong_type_tools)


def test_command_allowlist_constructor_validations() -> None:
    with pytest.raises(CommandAllowlistError):
        CommandAllowlist("invalid")  # type: ignore[arg-type]

    rule = TaskRule(name="ops", tools=("deploy",))
    with pytest.raises(CommandAllowlistError):
        CommandAllowlist({"": rule})
    with pytest.raises(CommandAllowlistError):
        CommandAllowlist({"ops": ("not", "rule")})  # type: ignore[arg-type, dict-item]
    with pytest.raises(CommandAllowlistError):
        CommandAllowlist({})


def test_cli_enforces_allowlist() -> None:
    from gabriel.ui import cli as cli_module

    original = cli_module._COMMAND_ALLOWLIST
    try:
        restricted = CommandAllowlist.from_mapping({"arithmetic": ["add"]})
        cli_module.configure_command_allowlist(restricted)

        cli_module.main(["add", "1", "2"])

        with pytest.raises(SystemExit) as excinfo:
            cli_module.main(["multiply", "2", "2"])
        assert "not allow-listed" in str(excinfo.value)
    finally:
        cli_module.configure_command_allowlist(original)


def test_cli_enforces_secret_allowlist() -> None:
    from gabriel.ui import cli as cli_module

    original = cli_module._COMMAND_ALLOWLIST
    try:
        restricted = CommandAllowlist.from_mapping({"secrets": ["secret.store"]})
        cli_module.configure_command_allowlist(restricted)

        with pytest.raises(SystemExit) as excinfo:
            cli_module.main(["secret", "get", "svc", "user"])
        assert "not allow-listed" in str(excinfo.value)
    finally:
        cli_module.configure_command_allowlist(original)
