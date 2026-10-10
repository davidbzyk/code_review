---
id: crosscutting/testing
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Testing"
description: "Where tests live and how they are run."
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
  - resource: src-tauri/src/pipeline.rs
  - resource: src-tauri/src/ffmpeg.rs
  - resource: src-tauri/sidecar/test_binary.sh
related:
  - deployment/quality-gates
  - deployment/build-and-run
---
# Testing

Tests exist for the frontend library, the Rust modules and the packaged sidecar.

## Facts

- Vitest runs `src/**/*.{test,spec}.{js,ts}` in jsdom with `vitest-setup.ts`; coverage covers `src/lib/**` with thresholds 50 (statements, branches, lines) and 55 (functions) (vitest.config.ts).
- Frontend test files: src/lib/state.svelte.test.ts, src/lib/recorder.test.ts, src/lib/logger.test.ts.
- Rust unit tests sit in `#[cfg(test)] mod tests` blocks inside the source files (for example pipeline.rs, ffmpeg.rs, config.rs, secrets.rs).
- `test_binary.sh` exercises the built sidecar binary (src-tauri/sidecar/test_binary.sh).
- `test:rust:coverage` runs `cargo llvm-cov` and ignores `lib.rs`, `main.rs` and `commands/window.rs`.
- Recorder code needing a browser is wrapped in `v8 ignore` comments.

## Related

- [[deployment/quality-gates]]
- [[deployment/build-and-run]]
