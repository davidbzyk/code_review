---
id: crosscutting/testing
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Testing"
description: "Test frameworks, test files and coverage thresholds."
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
  - resource: src/lib/state.svelte.test.ts
  - resource: src/lib/recorder.test.ts
  - resource: src/lib/logger.test.ts
  - resource: package.json
  - resource: src-tauri/src/ffmpeg.rs
  - resource: src-tauri/src/elevenlabs.rs
related:
  - deployment/ci-and-hooks
---
# Testing

Frontend tests use Vitest; Rust tests sit in `#[cfg(test)]` modules.

## Frontend
- `vitest.config.ts`: jsdom environment, include `src/**/*.{test,spec}.{js,ts}`, setup file `vitest-setup.ts` (imports `@testing-library/jest-dom/vitest`).
- Coverage provider `v8`; thresholds statements 50, branches 50, functions 55, lines 50; scope `src/lib/**`.
- Test files: src/lib/state.svelte.test.ts, src/lib/recorder.test.ts, src/lib/logger.test.ts.
- `recorder.svelte.ts` marks browser-only code with `v8 ignore start` and `v8 ignore stop`.

## Rust
- Unit tests in modules such as src-tauri/src/ffmpeg.rs (argument builders) and src-tauri/src/elevenlabs.rs (URL and constant checks).
- `pnpm test:rust` runs `cargo test`; `pnpm test:rust:coverage` runs `cargo llvm-cov` (package.json).

## Related
- [CI and Git Hooks](../deployment/ci-and-hooks.md)
