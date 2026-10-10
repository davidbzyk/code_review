---
id: crosscutting/testing
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Testing"
description: "Frontend and Rust test setup."
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
  - resource: package.json
  - resource: src-tauri/src/commands/recording.rs
relations:
  relates_to:
    - deployment/ci-and-hooks
---

Frontend tests use Vitest with jsdom; Rust tests are `#[cfg(test)]` modules in the source files.

## Facts

- `vitest.config.ts` includes `src/**/*.{test,spec}.{js,ts}` and `src/**/*.svelte.{test,spec}.{js,ts}`, environment `jsdom`, setup file `vitest-setup.ts`.
- `vitest-setup.ts` imports `@testing-library/jest-dom/vitest`.
- Coverage provider `v8` over `src/lib/**`, thresholds statements 50, branches 50, functions 55, lines 50.
- Test files: `src/lib/state.svelte.test.ts`, `src/lib/recorder.test.ts`, `src/lib/logger.test.ts`.
- `recorder.svelte.ts` marks browser-only blocks with `/* v8 ignore start */`.
- Rust modules with tests: `config.rs`, `elevenlabs.rs`, `ffmpeg.rs`, `google_drive.rs`, `pipeline.rs`, `prerequisites.rs`, `secrets.rs`, `commands/recording.rs`.
- `package.json`: `test`, `test:rust` (`cd src-tauri && cargo test`), `test:all`, and coverage scripts (`cargo llvm-cov` with an ignore regex for `lib`, `main` and `commands/window.rs`).

## Related

- [CI and hooks](../deployment/ci-and-hooks.md)
