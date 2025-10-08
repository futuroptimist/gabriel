# jobbot3000 Threat Model

The **jobbot3000** project automates job searches, resume generation, and interview prep.

## Current Snapshot (2025-10-08)

- **Operational context:** Node CLI with Playwright/LLM helpers filters job boards, paginates results,
  and produces deliverables.
- **Key changes since 2025-09-29:** Track filters/pagination (PR #757) expanded API usage and added
  new GitHub workflows plus Dependabot config tweaks.
- **Risks to monitor:** Filtering logic may store personal search queries; ensure logs sanitize job
  descriptions and tokens as new workflows execute.

## Threats

- **Data leakage:** Resume PDFs and transcripts may contain sensitive personal information.
- **Token compromise:** API keys for job boards or OpenAI could leak via logs.
- **Automation drift:** Scripts that auto-apply to jobs might send stale or incorrect info.

## Mitigations

- Provide clear retention policies and default to deleting generated artifacts after export.
- Mask tokens in logs and use environment variables rather than checked-in config.
- Keep tests covering output bundles to ensure required files (like `resume.pdf`) are present.
