---
id: crosscutting/testing
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Testing
description: Test frameworks, locations and the commands that run them.
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
  - resource: lefthook.yml
  - resource: src-tauri/Cargo.toml
  - resource: src-tauri/src/tts_provider.rs
  - resource: src-tauri/src/prerequisites.rs
related:
  - deployment/ci-and-hooks
  - building-blocks/frontend-state-and-config
---

# Testing

Three test suites exist, one per language.

## Facts

- TypeScript: Vitest with jsdom, files `src/lib/logger.test.ts`, `recorder.test.ts`, `voicebox.test.ts`, `state.svelte.test.ts` (vitest.config.ts, package.json `test`).
- `vitest-setup.ts` is the setup file; libraries `@testing-library/svelte` and `jest-dom` are dev dependencies.
- Rust: unit tests in `#[cfg(test)] mod tests` blocks inside source files, for example src-tauri/src/tts_provider.rs and src-tauri/src/prerequisites.rs; `filetime` is a dev dependency; run with `cargo test` (`pnpm test:rust`).
- Python: `test_tts.py`, `test_chunked_tts.py`, `test_server_integration.py` and `test_binary.sh` in src-tauri/sidecar.
- Coverage: `pnpm test:coverage`, and `cargo llvm-cov` in `test:rust:coverage` with an ignore regex for `lib.rs`, `main.rs`, `commands/window.rs`.
- Hooks and CI run the suites (lefthook.yml).

## Related

- [CI and Git Hooks](../deployment/ci-and-hooks.md)
- [Frontend State and Config](../building-blocks/frontend-state-and-config.md)
