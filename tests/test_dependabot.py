from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any, cast


def test_dependabot_monitors_github_actions() -> None:
    config_path = Path(".github/dependabot.yml")
    yaml = importlib.import_module("yaml")
    config = cast(dict[str, Any], yaml.safe_load(config_path.read_text()))

    updates_raw = config.get("updates", [])
    assert isinstance(updates_raw, list), "Dependabot updates should be a list."
    updates = cast(list[dict[str, Any]], updates_raw)
    assert updates, "Dependabot configuration must define at least one update entry."

    ecosystems = {entry.get("package-ecosystem") for entry in updates}
    assert "pip" in ecosystems, "Python dependencies should remain monitored."

    actions_entries = [
        entry for entry in updates if entry.get("package-ecosystem") == "github-actions"
    ]
    assert actions_entries, "Dependabot should monitor GitHub Actions updates."

    actions_config = actions_entries[0]
    assert actions_config.get("directory") == "/"
    schedule = actions_config.get("schedule", {})
    assert schedule.get("interval") == "weekly"
