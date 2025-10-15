from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_readme_includes_docker_commands() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "docker build -t gabriel ." in readme  # nosec B101
    assert "docker run --rm -it gabriel gabriel-calc add 2 3" in readme  # nosec B101
    assert '-v "$(pwd)/secrets:/app/secrets"' in readme  # nosec B101


def test_faq_answers_docker_usage() -> None:
    faq = (ROOT / "docs/gabriel/FAQ.md").read_text(encoding="utf-8")
    assert "Can I run Gabriel entirely inside Docker?" in faq  # nosec B101
    assert re.search(r"README section\s+titled \*Docker builds\*", faq)  # nosec B101


def test_readme_documents_viewer_cli() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "gabriel viewer" in readme  # nosec B101


def test_codex_implement_prompt_alias_is_present() -> None:
    prompt_path = ROOT / "docs/prompts/codex/implement.md"
    contents = prompt_path.read_text(encoding="utf-8")
    assert "Implement Mentioned Feature Prompt" in contents  # nosec B101
    assert "Implement Requested Feature Prompt" in contents  # nosec B101
    assert "legacy links" in contents  # nosec B101
