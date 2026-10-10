---
id: crosscutting/testing
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Testing
description: Tests exist for the frontend (vitest), Rust modules (cargo test) and the sidecar (pytest), run by hooks and CI.
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
  - resource: .github/workflows/ci.yml
  - resource: src/lib/state.svelte.test.ts
  - resource: src/lib/recorder.test.ts
  - resource: src/lib/voicebox.test.ts
  - resource: src/lib/logger.test.ts
  - resource: src-tauri/sidecar/test_tts.py
  - resource: src-tauri/sidecar/test_chunked_tts.py
  - resource: src-tauri/sidecar/test_server_integration.py
related:
  - building-blocks/build-scripts
  - deployment/build-and-packaging
  - crosscutting/logging
---

# Testing

Three test suites run from package scripts, git hooks and a GitHub workflow.

## Facts

- Frontend: vitest with `jsdom`, setup file `vitest-setup.ts` (imports `@testing-library/jest-dom/vitest`), tests in `src/**/*.{test,spec}.{js,ts}`; coverage thresholds statements 50, branches 50, functions 55, lines 50 (vitest.config.ts).
- Scripts: `test`, `test:coverage`, `test:rust` (`cargo test`), `test:all` (package.json).
- Rust: `#[cfg(test)]` modules inside source files, with `filetime` as a dev dependency (src-tauri/Cargo.toml).
- Sidecar: `test_tts.py`, `test_chunked_tts.py`, `test_server_integration.py`, and `test_binary.sh` for the frozen binary.
- `lefthook.yml` pre-commit: frontend tests, cargo tests, sidecar pytest for two files, `pnpm check`; pre-push: clippy and audits.
- `.github/workflows/ci.yml` has a `frontend` job (ubuntu, pnpm 10, node 22: check, test, audit) and a `rust` job (macOS: placeholder sidecars, clippy, test, cargo audit).

## Related

- [[building-blocks/build-scripts]] - Build and tooling scripts
- [[deployment/build-and-packaging]] - Build and packaging
- [[crosscutting/logging]] - Logging
