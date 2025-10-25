"""Command allowlist registry used to gate CLI tool execution."""

from __future__ import annotations

import fnmatch
import importlib
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Protocol, cast

__all__ = [
    "CommandAllowlist",
    "CommandAllowlistError",
    "CommandNotAllowedError",
    "TaskRule",
    "load_default_allowlist",
]


yaml = cast("_YamlModule", importlib.import_module("yaml"))


class CommandAllowlistError(RuntimeError):
    """Raised when the command allowlist cannot be loaded or validated."""


class CommandNotAllowedError(CommandAllowlistError):
    """Raised when a task attempts to execute a tool outside the allowlist."""

    def __init__(self, task: str, tool: str, message: str | None = None):
        """Initialise the error with the denied ``task``/``tool`` combination."""
        formatted = message or f"Tool '{tool}' is not allow-listed for task '{task}'."
        super().__init__(formatted)
        self.task = task
        self.tool = tool


@dataclass(frozen=True, slots=True)
class TaskRule:
    """Represents the allow-listed tools for a specific task."""

    name: str
    tools: tuple[str, ...]
    description: str | None = None

    def __post_init__(self) -> None:
        """Normalise tool patterns and validate task metadata."""
        normalized: list[str] = []
        seen: set[str] = set()
        for tool in self.tools:
            if not isinstance(tool, str) or not tool.strip():
                raise CommandAllowlistError(
                    f"Task '{self.name}' includes an invalid tool entry: {tool!r}"
                )
            candidate = tool.strip()
            if candidate in seen:
                raise CommandAllowlistError(
                    f"Task '{self.name}' defines duplicate tool entry '{candidate}'"
                )
            normalized.append(candidate)
            seen.add(candidate)
        object.__setattr__(self, "tools", tuple(normalized))
        if self.description is not None:
            description = self.description.strip()
            object.__setattr__(self, "description", description or None)

    def matches(self, tool: str) -> bool:
        """Return ``True`` when ``tool`` matches one of the allow-listed patterns."""

        candidate = tool.strip()
        return any(fnmatch.fnmatchcase(candidate, pattern) for pattern in self.tools)


class CommandAllowlist:
    """In-memory registry of tasks mapped to their allow-listed tools."""

    __slots__ = ("_tasks", "source")

    def __init__(self, tasks: Mapping[str, TaskRule], *, source: Path | None = None) -> None:
        """Create a registry from validated task rules."""
        if not isinstance(tasks, Mapping):
            raise CommandAllowlistError("Allowlist tasks must be provided as a mapping")
        normalized: dict[str, TaskRule] = {}
        for task, rule in tasks.items():
            if not isinstance(task, str) or not task.strip():
                raise CommandAllowlistError("Task names must be non-empty strings")
            if not isinstance(rule, TaskRule):
                raise CommandAllowlistError(
                    f"Task '{task}' must be associated with a TaskRule instance"
                )
            normalized[task.strip()] = rule
        if not normalized:
            raise CommandAllowlistError("Command allowlist must include at least one task entry")
        self._tasks: Mapping[str, TaskRule] = dict(sorted(normalized.items()))
        self.source: Path | None = source

    @classmethod
    def from_file(cls, path: Path | str) -> CommandAllowlist:
        """Load an allowlist from ``path`` and return a validated registry."""

        allowlist_path = Path(path)
        try:
            raw = allowlist_path.read_text(encoding="utf-8")
        except FileNotFoundError as exc:  # pragma: no cover - exercised indirectly
            raise CommandAllowlistError(f"Allowlist file not found: {allowlist_path}") from exc

        try:
            document = yaml.safe_load(raw) or {}
        except yaml.YAMLError as exc:  # pragma: no cover - validated by tests
            raise CommandAllowlistError(
                f"Failed to parse YAML from {allowlist_path}: {exc}"
            ) from exc

        if not isinstance(document, dict):
            raise CommandAllowlistError(
                "Allowlist file root must be a mapping of sections to configuration"
            )

        tasks_section = document.get("tasks")
        if tasks_section is None:
            raise CommandAllowlistError("Allowlist file is missing required 'tasks' mapping")
        if not isinstance(tasks_section, Mapping) or not tasks_section:
            raise CommandAllowlistError("'tasks' must be a mapping with at least one entry")

        tasks: dict[str, TaskRule] = {}
        for name, config in tasks_section.items():
            if not isinstance(name, str) or not name.strip():
                raise CommandAllowlistError("Task names within the allowlist must be strings")
            if not isinstance(config, Mapping):
                raise CommandAllowlistError(
                    f"Task '{name}' configuration must be a mapping with task metadata"
                )
            description = config.get("description")
            if description is not None and not isinstance(description, str):
                raise CommandAllowlistError(
                    f"Task '{name}' description must be a string when provided"
                )
            tools = config.get("tools")
            if tools is None:
                raise CommandAllowlistError(
                    f"Task '{name}' configuration must include a 'tools' collection"
                )
            if not isinstance(tools, list) or not tools:
                raise CommandAllowlistError(
                    f"Task '{name}' tools must be a non-empty list of strings"
                )
            tasks[name.strip()] = TaskRule(
                name=name.strip(),
                tools=tuple(str(item) for item in tools),
                description=description,
            )

        return cls(tasks, source=allowlist_path)

    @classmethod
    def from_mapping(
        cls, mapping: Mapping[str, Iterable[str]], *, description: Mapping[str, str] | None = None
    ) -> CommandAllowlist:
        """Construct an allowlist from a simple mapping of tasks to tools."""

        descriptions = description or {}
        tasks: dict[str, TaskRule] = {}
        for task, tools in mapping.items():
            if not isinstance(task, str) or not task.strip():
                raise CommandAllowlistError("Task names must be non-empty strings")
            if not isinstance(tools, Iterable):
                raise CommandAllowlistError(
                    f"Tools for task '{task}' must be an iterable of strings"
                )
            normalized_tools: list[str] = []
            for item in tools:
                if not isinstance(item, str) or not item.strip():
                    raise CommandAllowlistError(
                        f"Tools for task '{task}' must be non-empty strings"
                    )
                normalized_tools.append(item.strip())
            task_description = descriptions.get(task.strip()) if descriptions else None
            tasks[task.strip()] = TaskRule(
                name=task.strip(), tools=tuple(normalized_tools), description=task_description
            )
        return cls(tasks)

    def is_allowed(self, task: str, tool: str) -> bool:
        """Return ``True`` when ``tool`` is allowed for ``task``."""

        rule = self._tasks.get(task.strip())
        if rule is None:
            return False
        return rule.matches(tool)

    def require_allowed(self, task: str, tool: str) -> None:
        """Raise :class:`CommandNotAllowedError` when ``tool`` is not allow-listed."""

        rule = self._tasks.get(task.strip())
        if rule is None:
            raise CommandNotAllowedError(
                task,
                tool,
                message=(
                    f"Task '{task}' is not defined in the command allowlist"
                    + (f" loaded from {self.source}" if self.source else "")
                ),
            )
        if not rule.matches(tool):
            allowed = ", ".join(rule.tools)
            raise CommandNotAllowedError(
                task,
                tool,
                message=(
                    f"Tool '{tool}' is not allow-listed for task '{task}'. "
                    f"Allowed tools: {allowed}"
                ),
            )

    def tools_for(self, task: str) -> tuple[str, ...]:
        """Return the allow-listed tools for ``task`` or an empty tuple when missing."""

        rule = self._tasks.get(task.strip())
        if rule is None:
            return ()
        return rule.tools

    @property
    def tasks(self) -> tuple[str, ...]:
        """Return all known tasks sorted alphabetically."""

        return tuple(self._tasks.keys())


def load_default_allowlist() -> CommandAllowlist:
    """Load the package's default allowlist configuration."""

    resource = resources.files("gabriel").joinpath("config", "command_allowlist.yaml")
    try:
        with resources.as_file(resource) as path:
            return CommandAllowlist.from_file(path)
    except FileNotFoundError as exc:  # pragma: no cover - defensive
        raise CommandAllowlistError(
            "Default command allowlist resource is missing from the package"
        ) from exc


class _YamlModule(Protocol):
    YAMLError: type[Exception]

    def safe_load(self, stream: str) -> object:  # pragma: no cover - exercised indirectly
        ...
