---
id: crosscutting/static-checks
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Static checks and tests"
description: "Type checking configuration; no test files are present."
domain: architecture
tags:
  - crosscutting
  - testing
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
architecture_layer: crosscutting
sources:
  - resource: package.json
  - resource: tsconfig.json
  - resource: PROJECT_RULES.md
related:
  - solution-strategy/technologies
  - deployment/build-and-package
---

# Static checks and tests

Checks are `svelte-check` with a strict TypeScript config; the tree holds no test files.

## Facts
- Script `check` runs `svelte-kit sync && svelte-check --tsconfig ./tsconfig.json` (package.json).
- `tsconfig.json` extends `.svelte-kit/tsconfig.json` and sets `strict`, `checkJs`, `allowJs` (tsconfig.json).
- `PROJECT_RULES.md` lists rules R-01 to R-11 for frontend, Rust and a Python sidecar.
- No file under src/ or src-tauri/src/ matches `*.test.ts`, and package.json defines no test script.

## Related

- [[solution-strategy/technologies]]
- [[deployment/build-and-package]]
