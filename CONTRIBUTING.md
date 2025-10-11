# Contributing

We welcome pull requests that improve Gabriel's security posture, documentation, or functionality. Before contributing, please:

1. Read [`AGENTS.md`](AGENTS.md) for repository-specific automation rules.
2. Ensure any code changes support Python 3.10+ and include minimal tests with `pytest` when applicable.
3. Document new behavior in `README.md` or under `docs/`.
4. Use `uv` for dependency management and run `flake8` and `bandit` locally to catch style and security issues.
5. Complete the pull request template, including the prompt-injection review checklist aligned with
   OWASP LLM01–LLM10.

By contributing you agree to license your work under the repository's MIT license.
