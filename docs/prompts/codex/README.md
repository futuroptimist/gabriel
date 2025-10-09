# Prompt Templates

This directory collects example prompts for using an LLM with Gabriel. These prompts are exploratory and will evolve.

## Prompt Catalog

- [Scan for Bright and Dark Patterns](scan-bright-dark-patterns.md)
- [Generate Improvement Checklist Items](generate-improvements.md)
- [Implement Mentioned Feature](implement.md)
- [Update Flywheel Risk Model](update-risk-model.md)
- [Refresh Related Project Knowledge](refresh-related-projects.md)

## Example: Summarize Security Posture

```text
You are Gabriel, a privacy-first assistant. Given the following system overview, identify potential security gaps and suggest mitigations.

<system_overview>
...paste output from inventory scripts here...
</system_overview>
```

Contributions of new prompt templates are welcome. Keep them general and avoid leaking personal information.
