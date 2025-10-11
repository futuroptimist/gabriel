# Roadmap

This document outlines tentative phases for Gabriel. Dates are aspirational and subject to change.

## Phase 0: Foundation

- Add project documentation (README, FAQ, AGENTS).
- Outline security best practice checklists.
- Provide minimal CLI or script scaffolding for experiments.

## Phase 1: Local Security Advisor

- Collect user-consented configuration data.
- Suggest improvements for self-hosted services such as PhotoPrism and VaultWarden.
  (VaultWarden checks ship in `gabriel.selfhosted`.)
- Integrate token.place for local LLM inference. (`TokenPlaceClient` now wraps relay requests.)

## Phase 2: Personal Knowledge Manager

- Organize user notes and security data into a searchable store.
- Provide advanced LLM-driven recommendations.
- Explore synergy with [sigma](https://github.com/futuroptimist/sigma) as a push-to-talk interface for local LLM interactions.

## Phase 3+: Real World Monitoring (long term)

- Introduce optional home monitoring via sensors or robotics.
- Emphasize privacy, encryption, and user control at all times.
