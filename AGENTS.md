# Instructions for LLM Contributors

This repository welcomes improvements from automated agents and human contributors. Please follow these guidelines:

* Keep user privacy and security central. Avoid adding analytics or unapproved network calls.
* Use lightweight, well-understood dependencies. Discuss heavy additions before including them.
* Update documentation (`README.md`, files under `docs/`) whenever behavior or design changes.
* If you introduce code, prefer Python 3.10+ and standard tooling. Provide a `requirements.txt` if dependencies are needed.
* A minimal test suite exists. Ensure it passes by running `pytest` with coverage before opening a PR.
* Summaries and PR messages should include citations to relevant files.
* Append new questions to `docs/FAQ.md` rather than removing existing items.
* Run `pytest` to confirm tests pass (even if none are collected) before opening a PR.
