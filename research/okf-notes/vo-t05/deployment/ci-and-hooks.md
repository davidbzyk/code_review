---
id: deployment/ci-and-hooks
schema: okf/schemas/v1/architecture.json
type: Architecture
title: CI and Git Hooks
description: The GitHub Actions workflow and lefthook hooks that run checks and tests.
domain: architecture
tags:
  - deployment
  - ci
  - testing
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: .github/workflows/ci.yml
  - resource: lefthook.yml
  - resource: vitest.config.ts
  - resource: vitest-setup.ts
  - resource: package.json
related:
  - crosscutting/testing
  - deployment/build-and-packaging
---

# CI and Git Hooks

CI runs on push and pull request to `main` (.github/workflows/ci.yml).

## Jobs

- `frontend` (ubuntu-latest): pnpm 10, Node 22, `pnpm install --frozen-lockfile`, `pnpm check`, `pnpm test`, `pnpm audit --audit-level=high` (continue on error).
- `rust` (macos-latest): stable toolchain with clippy, creates empty placeholder files `src-tauri/binaries/ffmpeg-aarch64-apple-darwin` and `voiceover-tts-aarch64-apple-darwin`, runs `cargo clippy -- -D warnings`, `cargo test`, `cargo audit`.

## lefthook.yml

- `pre-commit` (parallel): `pnpm test`, `cd src-tauri && cargo test`, sidecar pytest on `test_tts.py` and `test_chunked_tts.py` using `.sidecar-venv`, and `pnpm check`.
- `pre-push` (parallel): `cargo clippy -D warnings`, `pnpm audit`, `cargo audit`.
- `package.json` script `prepare` runs `lefthook install`.

## Vitest

- `vitest.config.ts`: jsdom environment, setup file `vitest-setup.ts`, includes `src/**/*.{test,spec}.{js,ts}`, v8 coverage over `src/lib` with thresholds 50 statements, 50 branches, 55 functions, 50 lines.

## Related

- [Testing](../crosscutting/testing.md)
- [Build and Packaging](./build-and-packaging.md)
