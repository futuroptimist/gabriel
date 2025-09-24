# Suggested Improvements for PR Reaper

This document collects recommended enhancements for the [pr-reaper](https://github.com/futuroptimist/pr-reaper) repository.

## Current Snapshot (2025-09-24)

- **Status:** ✅ in the Futuroptimist related projects list
- **Focus:** GitHub Action that bulk-closes your own stale pull requests with a dry-run safety
  valve.
- **Primary integration:** Works across repositories bootstrapped from the `flywheel` template.

## Checklist

- [ ] Add configuration examples for filtering by label, branch pattern, and repository owner.
- [ ] Document dry-run telemetry to reassure maintainers before enabling destructive mode.
- [ ] Provide guidance on combining PR archiving with Dependency Review workflows.
