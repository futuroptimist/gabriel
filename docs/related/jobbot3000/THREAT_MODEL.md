# jobbot3000 Threat Model

jobbot3000 automates job discovery and application tracking for self-hosted seekers.
This document outlines the current threat considerations.

## Current Snapshot (2025-09-24)

- **Automations:** Scrapes job boards, enriches listings with LLM summaries, and stores
  application tasks locally.
- **Data sensitivity:** Handles resumes, cover letters, and employer communications that may
  contain personally identifiable information.

## Security Assumptions

- The service runs on user-controlled infrastructure with encrypted storage for personal data.
- External integrations (email, calendars, ATS APIs) use scoped credentials stored outside source
  control.

## Potential Risks

- Improperly secured storage could leak resumes or job history.
- Automated scraping may trigger IP blocking or legal concerns without rate limiting.
- Prompt injections in scraped listings could manipulate downstream LLM summarization steps.
