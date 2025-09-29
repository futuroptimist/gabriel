# jobbot3000 Threat Model

The **jobbot3000** project automates job searches, resume generation, and interview prep.

## Current Snapshot (2025-09-29)

- **Operational context:** Node CLI ingests postings, runs LLM prompts, and outputs deliverables.
- **Key changes since 2025-09-24:** Resume bundle enforcement and expanded docs/workflows increased
  the scope of automation but did not introduce new external services.
- **Risks to monitor:** Handling of personal data (resumes, transcripts), token scopes for scraping
  APIs, and CLI storage paths.

## Threats

- **Data leakage:** Resume PDFs and transcripts may contain sensitive personal information.
- **Token compromise:** API keys for job boards or OpenAI could leak via logs.
- **Automation drift:** Scripts that auto-apply to jobs might send stale or incorrect info.

## Mitigations

- Provide clear retention policies and default to deleting generated artifacts after export.
- Mask tokens in logs and use environment variables rather than checked-in config.
- Keep tests covering output bundles to ensure required files (like `resume.pdf`) are present.
