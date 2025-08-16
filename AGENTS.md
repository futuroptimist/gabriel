# Gabriel Agents Guidelines

> Guidance for OpenAI Codex and human contributors. These instructions follow the [AGENTS.md spec](https://gist.github.com/dpaluy/cc42d59243b0999c1b3f9cf60dfd3be6) and the [Agents.md Guide](https://agentsmd.net/).

## Overview

- Prioritise user privacy and security. Avoid analytics or network calls unless discussed.
- Use lightweight Python 3.10+ dependencies. Document them in `requirements.txt`.
- Keep documentation (`README.md`, `docs/`) updated with any behavior or design change.
- Add meaningful variable and function names and include docstrings for complex logic.
- Follow PEP8 style; run `pre-commit run --all-files` before committing.
- Append questions to `docs/gabriel/FAQ.md` rather than removing existing items.

## Testing Requirements

Run the full test suite before submitting changes:

```bash
pre-commit run --all-files
pytest --cov=gabriel --cov-report=term-missing
```

## Pull Request Guidelines

1. Clearly describe the change and reference relevant issues.
2. Ensure all tests pass and include screenshots for UI changes if applicable.
3. Keep PRs focused on a single concern and include citations in the description.

## Programmatic Checks

All checks above must pass prior to merging. This helps maintain code quality and security.
