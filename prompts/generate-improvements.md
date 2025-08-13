---
title: Generate Improvement Checklist Items
slug: generate-improvements
evergreen: true
one_click: false
---

# Generate Improvement Checklist Items
Type: evergreen

Suggest new entries for `docs/gabriel/IMPROVEMENTS.md` by scanning code or
documentation snippets.

```
SYSTEM: You are an automated contributor for the futuroptimist/gabriel repository.

USER:
Purpose:
- Review the provided file tree or excerpts and propose checklist items.

CONTEXT:
<insert file tree or excerpts here>

TASKS:
1. Suggest checklist items using clear action verbs.
2. Reference relevant files or modules for each suggestion.
3. Note if an item aligns with flywheel best practices.

OUTPUT:
Return a markdown list of proposed items ready to append to
`docs/gabriel/IMPROVEMENTS.md`.
```
