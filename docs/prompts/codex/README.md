# Prompt Templates

This directory collects example prompts for using an LLM with Gabriel. These prompts are exploratory and will evolve.

## Prompt Catalog

- [Baseline Codex Automation Prompt](baseline-automation.md)
- [Scan for Bright and Dark Patterns](scan-bright-dark-patterns.md)
- [Generate Improvement Checklist Items](generate-improvement-checklists.md)
- [Implement Requested Feature](implement-requested-feature.md)
- [Scan Related Repositories](scan-related-repositories.md)
- [Refresh Related Project Knowledge](refresh-related-project-knowledge.md)
- [Update Flywheel Risk Model](update-flywheel-risk-model.md)
- [Polish Four-Module Architecture](polish.md)

## Example: Summarize Security Posture

```text
You are Gabriel, a privacy-first assistant. Given the following system overview, identify potential security gaps and suggest mitigations.

<system_overview>
...paste output from inventory scripts here...
</system_overview>
```

Contributions of new prompt templates are welcome. Keep them general and avoid leaking personal information.
