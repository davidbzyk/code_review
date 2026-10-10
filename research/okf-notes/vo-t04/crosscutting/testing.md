---
id: crosscutting/testing
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Testing"
description: "Vitest runs the TypeScript unit tests in jsdom, cargo test runs the in-file Rust tests, and lefthook runs both before each commit."
domain: architecture
tags:
  - crosscutting
  - testing
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: vitest.config.ts
  - resource: vitest-setup.ts
  - resource: lefthook.yml
  - resource: package.json
  - resource: src/lib/state.svelte.test.ts
  - resource: src/lib/recorder.test.ts
  - resource: src/lib/logger.test.ts
relations:
  relates_to:
    - deployment/build-and-package
    - crosscutting/logging
---
# Testing

Tests sit beside the code they exercise.

## Frontend

- vitest.config.ts: includes `src/**/*.{test,spec}.{js,ts}` and `src/**/*.svelte.{test,spec}.{js,ts}`, uses `jsdom` and setup file vitest-setup.ts (which imports `@testing-library/jest-dom/vitest`).
- Coverage: provider `v8`, files under `src/lib/`, thresholds 50 statements, 50 branches, 55 functions, 50 lines.
- Test files: src/lib/state.svelte.test.ts, src/lib/recorder.test.ts, src/lib/logger.test.ts.
- src/lib/recorder.svelte.ts marks browser-only blocks with `/* v8 ignore start */`.

## Rust

- `#[cfg(test)]` modules sit inside src-tauri/src/commands/recording.rs and src-tauri/src/prerequisites.rs; `pnpm test:rust` runs `cd src-tauri && cargo test`.
- `test:rust:coverage` uses `cargo llvm-cov` and ignores `lib|main.rs` and `commands/window.rs` (package.json).

## Hooks

lefthook.yml runs `frontend-tests`, `rust-tests` and `typecheck` in parallel on pre-commit.

## Related

[[deployment/build-and-package]], [[crosscutting/logging]]
