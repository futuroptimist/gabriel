# Instructions for LLM Contributors

This repository welcomes improvements from automated agents and human contributors. Please follow these guidelines:

* Keep user privacy and security central. Avoid adding analytics or unapproved network calls.
* Use lightweight, well-understood dependencies. Discuss heavy additions before including them.
* Update documentation (`README.md`, files under `docs/`) whenever behavior or design changes.
* If you introduce code, prefer Python 3.10+ and standard tooling. Provide a `requirements.txt` if dependencies are needed.
* There are currently no automated tests. Mention this in your PR summary and consider adding tests using `pytest`.
* Summaries and PR messages should include citations to relevant files.
* Append new questions to `docs/FAQ.md` rather than removing existing items.
