"""Tests ensuring CI workflows cache Python dependencies."""

from pathlib import Path

WORKFLOW_PATHS = (
    Path(".github/workflows/ci.yml"),
    Path(".github/workflows/coverage.yml"),
    Path(".github/workflows/docs.yml"),
)


def test_workflows_use_cache_step() -> None:
    """Workflows should configure caching for uv dependencies."""

    for path in WORKFLOW_PATHS:
        contents = path.read_text(encoding="utf-8")
        assert "actions/cache@v4" in contents, f"Missing cache step in {path}"
        assert "~/.cache/uv" in contents, f"Cache path not configured in {path}"
