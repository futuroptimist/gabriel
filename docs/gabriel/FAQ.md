# FAQ

This FAQ lists questions we have for the maintainers and community. Answers will be filled in as the project evolves.

1. **Preferred programming languages and frameworks?**
   - No strict preference, but Python is recommended initially due to its strong machine learning ecosystem.
2. **Expected integration points with [token.place](https://github.com/futuroptimist/token.place)?**
   - Gabriel can run models locally on CPU/GPU or call token.place's encrypted inference API when desired.
3. **Guidelines for storing user data securely?**
   - Use robust `.gitignore` rules and pre-commit hooks. Encourage filesystem encryption and careful handling of secrets.
4. **Policies on network access or telemetry?**
   - Local only by default and encrypted at rest; no telemetry is sent upstream.
5. **How should we coordinate with other projects like dspace and f2clipboard?**
   - Focus on integrating token.place first. Additional collaborations may come later.
6. **Are there existing datasets or knowledge bases we can leverage?**
   - None specified yet, but community suggestions are welcome.
7. **What level of automated testing is required for contributions?**
   - Use GitHub Actions and pre-commit hooks. Tests with `pytest` are encouraged.
8. **Any contributor license agreements or code of conduct?**
   - The project is MIT licensed and a contributors guide will outline code of conduct.
9. **Are external contributions currently welcome, or is this in a closed alpha?**
   - Contributions are welcome via pull request.
10. **Desired repository structure or directories to avoid?**
   - Keep the layout intuitive; there are no forbidden directories at this time.
11. **Is there a defined threat model for Gabriel?**
   - See [THREAT_MODEL.md](THREAT_MODEL.md) for the latest threat model and security assumptions.
12. **How does the flywheel approach impact Gabriel's risk management?**
   - Risks and mitigations for continuous automation are described in [FLYWHEEL_RISK_MODEL.md](FLYWHEEL_RISK_MODEL.md).
13. **What new flywheel features require extra caution?**
- The `crawl` subcommand now collects commit data across repositories. Use read-only tokens and avoid scanning private repos without permission.
14. **What improvements are recommended for token.place integration?**
   - See [../related/token_place/IMPROVEMENTS.md](../related/token_place/IMPROVEMENTS.md) for suggested mitigations against relay compromise and network attacks.
15. **Why reference the Sword of Damocles in Gabriel's documentation?**
   - The parable illustrates the constant risk that accompanies greater resources and privilege online. [SWORD_OF_DAMOCLES.md](SWORD_OF_DAMOCLES.md) explains how Gabriel aims to alleviate that danger through local, privacy-first design.
16. **How is test coverage reported?**
   - Coverage reports are uploaded to [Codecov](https://about.codecov.io/) through a GitHub Actions workflow.

17. **How does Gabriel mitigate prompt-injection or hidden instruction attacks?**
   - Treat code, documentation, and dependencies as untrusted; review automated changes and run security scans before executing them.

Feel free to extend this list with additional questions or provide answers in follow-up pull requests.

18. **Can I run Gabriel entirely inside Docker?**
   - Yes. Build the image with `docker build -t gabriel .` and run commands such as
     `docker run --rm -it gabriel gabriel-calc add 2 3`. Mount volumes or supply `--env-file`
     when secrets or configuration should persist between runs. See the README section
     titled *Docker builds* for more recipes.
19. **Does Gabriel include phishing detection yet?**
   - A lightweight heuristic scanner in `gabriel.phishing` analyses pasted links for
     punycode, suspicious TLDs, HTTP usage, and lookalike domains. Extend it with
     additional rules as the roadmap advances.
20. **Can Gabriel audit my VaultWarden deployment?**
   - Yes. Use `gabriel.selfhosted.audit_vaultwarden` with a
     `VaultWardenConfig` snapshot to identify gaps from the checklist in
     [docs/IMPROVEMENT_CHECKLISTS.md](../IMPROVEMENT_CHECKLISTS.md#vaultwarden).
21. **How about Syncthing hardening?**
   - `gabriel.selfhosted.audit_syncthing` evaluates HTTPS, discovery, relay, and
     trusted device settings using the
     [Syncthing improvements checklist](../IMPROVEMENT_CHECKLISTS.md#syncthing).
