---
title: 'Codex Related Projects Refresh Prompt'
slug: 'codex-related-projects-refresh'
---

# Codex Related Projects Refresh Prompt
Type: evergreen

Use this prompt when Gabriel needs to rescan Futuroptimist's related projects roster and refresh
internal documentation.

```text
SYSTEM:
You are an automated contributor for the Gabriel repository.

PURPOSE:
Keep Gabriel's related-project snapshots aligned with Futuroptimist's README.

CONTEXT:
- Open https://github.com/futuroptimist#related-projects and capture the current repository list.
- For each repository:
  - Clone it into a temporary workspace.
  - Record the stack, notable conventions, and security posture deltas since the last snapshot.
  - Capture open risks, maintenance gaps, or ecosystem dependencies to watch.
- Update this repository accordingly:
  - Refresh docs/related/**/IMPROVEMENTS.md and THREAT_MODEL.md files with 2025-09-24-style
    status notes.
  - Extend README.md, prompts-repos.md, and any checklists referencing the repository roster.
  - Add new terminology to dict/allow.txt if spellcheck fails.
- Follow AGENTS.md instructions and repository conventions for commits and PRs.
- Ensure the following checks succeed:
  - pre-commit run --all-files
  - pytest --cov=gabriel --cov-report=term-missing

REQUEST:
1. Enumerate every repository listed under Futuroptimist's Related Projects.
2. Scan each repository and summarize changes relevant to Gabriel's docs.
3. Update all impacted files in this repository so the roster and guidance stay current.
4. Run the checks above.
5. Commit and open a pull request.

OUTPUT:
A pull request that refreshes Gabriel's related-project documentation and passes all checks.
```
