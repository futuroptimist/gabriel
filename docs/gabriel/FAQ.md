# FAQ

This FAQ lists questions we have for the maintainers and community. Answers will be filled in as the project evolves.

1. **Preferred programming languages and frameworks?**

   No strict preference, but Python is recommended initially due to its strong machine learning ecosystem.

2. **Expected integration points with [token.place](https://github.com/futuroptimist/token.place)?**

   Gabriel can run models locally on CPU/GPU or call token.place's encrypted inference API when desired.

3. **Guidelines for storing user data securely?**

   Use robust `.gitignore` rules and pre-commit hooks. Encourage filesystem encryption and careful handling of secrets.

4. **Policies on network access or telemetry?**

   Local only by default and encrypted at rest; no telemetry is sent upstream.

5. **How should we coordinate with other projects like dspace and f2clipboard?**

   Focus on integrating token.place first. Additional collaborations may come later.

6. **Are there existing datasets or knowledge bases we can leverage?**

   None specified yet, but community suggestions are welcome.

7. **What level of automated testing is required for contributions?**

   Use GitHub Actions and pre-commit hooks. Tests with `pytest` are encouraged.

8. **Any contributor license agreements or code of conduct?**

   The project is MIT licensed and a contributors guide will outline code of conduct.

9. **Are external contributions currently welcome, or is this in a closed alpha?**

   Contributions are welcome via pull request.

10. **Desired repository structure or directories to avoid?**

    Keep the layout intuitive; there are no forbidden directories at this time.

11. **Is there a defined threat model for Gabriel?**

    See [THREAT_MODEL.md](THREAT_MODEL.md) for the latest threat model and security assumptions.

12. **How does the flywheel approach impact Gabriel's risk management?**

    Risks and mitigations for continuous automation are described in [FLYWHEEL_RISK_MODEL.md](FLYWHEEL_RISK_MODEL.md).

13. **What new flywheel features require extra caution?**

    The `crawl` subcommand now collects commit data across repositories. Use read-only tokens and avoid scanning private repos without permission.

14. **What improvements are recommended for token.place integration?**

    See [../related/token_place/IMPROVEMENTS.md](../related/token_place/IMPROVEMENTS.md) for suggested mitigations against relay compromise and network attacks.

15. **Why reference the Sword of Damocles in Gabriel's documentation?**

    The parable illustrates the constant risk that accompanies greater resources and privilege online. [SWORD_OF_DAMOCLES.md](SWORD_OF_DAMOCLES.md) explains how Gabriel aims to alleviate that danger through local, privacy-first design.

16. **How is test coverage reported?**

    Coverage reports are uploaded to [Codecov](https://about.codecov.io/) through a GitHub Actions workflow.

17. **How does Gabriel mitigate prompt-injection or hidden instruction attacks?**

    Treat code, documentation, and dependencies as untrusted; review automated
    changes, run security scans, and ensure the `gabriel.prompt_lint`
    pre-commit hook passes before executing them.

18. **Can I run Gabriel entirely inside Docker?**

    Yes. Build the image with `docker build -t gabriel .` and run commands such as `docker run --rm -it gabriel gabriel-calc add 2 3`. Mount volumes or supply `--env-file` when secrets or configuration should persist between runs. See the README section titled *Docker builds* for more recipes.

19. **How can I organize recurring security notes?**

    Gabriel's roadmap now includes a lightweight knowledge store for Markdown notes.
    Use `gabriel.ingestion.knowledge.KnowledgeStore` to index local files and search by keyword
    or tag without sending data to external services. The helper extracts titles,
    tags, and contextual snippets so you can jump straight to remediation guidance.

20. **Does Gabriel include phishing detection yet?**

    A lightweight heuristic scanner in `gabriel.analysis.phishing` analyses pasted links for
    punycode, suspicious TLDs, HTTP usage, lookalike domains, known URL shorteners,
    unusual ports, redirect parameters that jump to other domains, and attachments with
    risky executable or archive extensions. Extend it with additional rules as the
    roadmap advances.

21. **How do I call token.place for encrypted inference?**

    Import `TokenPlaceClient` and point it at your relay. The helper signs requests with your API
    token, provides a `check_health()` probe, and normalizes responses into a simple
    `TokenPlaceCompletion` dataclass. Example:

    ```python
    from gabriel import TokenPlaceClient

    client = TokenPlaceClient("https://relay.local", api_key="tp_test_123")
    completion = client.infer("Summarize pending CVEs", model="llama3-70b")
    print(completion.text)
    ```

    The client keeps traffic on the configured relay URL so you can pair encrypted inference with
    Gabriel's offline-first design.

22. **Can Gabriel audit my VaultWarden deployment?**

    Yes. Use `gabriel.analysis.selfhosted.audit_vaultwarden` with a `VaultWardenConfig` snapshot to identify gaps from the checklist in [docs/IMPROVEMENT_CHECKLISTS.md](../IMPROVEMENT_CHECKLISTS.md#vaultwarden).

23. **How do I preview the bundled WebGL viewer?**

    Run `gabriel viewer` to launch a threaded HTTP server that opens your browser locally. Add
    `--no-browser` for headless systems or `--host 0.0.0.0` to share the preview on your LAN. See
    [VIEWER.md](VIEWER.md) for more automation-friendly patterns.

24. **How should I sanitize prompts pulled from external sources?**

    Call `gabriel.ingestion.text.sanitize_prompt` before handing text to a model. It strips HTML tags,
    Markdown image embeddings, and zero-width characters that attackers use for
    prompt-injection payloads. Pair it with `gabriel.prompt_lint` to flag instructions that
    attempt to bypass guardrails.

25. **Can Gabriel suggest which findings to tackle first?**

    Yes. Pass audit findings to `gabriel.analysis.recommendations.generate_recommendations` and
    optionally include knowledge notes from `gabriel.ingestion.knowledge.KnowledgeStore`. The helper
    scores each finding, blends in related notes for context, and honors `RiskTolerance`
    preferences so you can down-rank lower-severity items when appropriate.
