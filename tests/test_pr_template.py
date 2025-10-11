from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / ".github" / "PULL_REQUEST_TEMPLATE.md"


def test_pr_template_includes_prompt_injection_review() -> None:
    assert TEMPLATE.exists(), "PULL_REQUEST_TEMPLATE.md should exist for contributors"  # nosec B101
    content = TEMPLATE.read_text(encoding="utf-8")
    assert "Prompt Injection Review" in content  # nosec B101
    for code in [f"LLM0{i}" for i in range(1, 10)] + ["LLM10"]:
        assert code in content, f"Expected OWASP {code} reference in PR template"  # nosec B101
    assert "OWASP" in content  # nosec B101
