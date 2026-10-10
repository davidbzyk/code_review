---
id: crosscutting/testing
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Testing
description: Test runners, test locations and coverage settings.
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
  - resource: src-tauri/sidecar/test_binary.sh
relations:
  relates_to:
    - deployment/build-and-packaging
    - solution-strategy/technology-choices
---
# Testing

Each language has its own test runner, and `lefthook.yml` runs them before commits.

## Facts

- Frontend: Vitest, jsdom, setup file `vitest-setup.ts`; includes `src/**/*.{test,spec}.{js,ts}` and `src/**/*.svelte.{test,spec}.{js,ts}`. Coverage uses v8 over `src/lib/**` with thresholds 50 statements, 50 branches, 55 functions, 50 lines (`vitest.config.ts`).
- Frontend test files sit beside the code, for example `src/lib/state.svelte.test.ts`, `src/lib/recorder.test.ts`, `src/lib/voicebox.test.ts`.
- Rust: unit tests in `#[cfg(test)]` modules of the source files; `filetime` is a dev-dependency (`src-tauri/Cargo.toml`). Script `test:rust` runs `cargo test`.
- Sidecar: `test_tts.py`, `test_chunked_tts.py`, `test_server_integration.py` in `src-tauri/sidecar`; `test_binary.sh` tests the frozen binary.
- `package.json` scripts: `test`, `test:watch`, `test:coverage`, `test:rust`, `test:all`.
- `lefthook.yml` pre-commit runs frontend tests, `cargo test`, sidecar pytest and `pnpm check`.

## Related

- [Build and Packaging](../deployment/build-and-packaging.md)
- [Technology Choices](../solution-strategy/technology-choices.md)
