---
id: deployment/ci-and-hooks
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "CI and Git Hooks"
description: "The GitHub Actions workflow and lefthook hooks."
domain: architecture
tags:
  - deployment
  - ci
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: .github/workflows/ci.yml
  - resource: lefthook.yml
  - resource: package.json
related:
  - deployment/build-and-package
  - crosscutting/testing
---
# CI and Git Hooks

CI runs two jobs on pushes and pull requests to `main`; lefthook runs checks before commit and push.

## .github/workflows/ci.yml
- Job `frontend` on `ubuntu-latest`: pnpm 10, Node 22, `pnpm install --frozen-lockfile`, `pnpm check`, `pnpm test`, `pnpm audit --audit-level=high` with `continue-on-error`.
- Job `rust` on `macos-latest`: stable toolchain with clippy, `Swatinem/rust-cache`, creates the placeholder `src-tauri/binaries/ffmpeg-aarch64-apple-darwin`, then `cargo clippy -- -D warnings`, `cargo test`, `cargo install cargo-audit`, `cargo audit`.

## lefthook.yml
- `pre-commit` (parallel): `pnpm test`, `cd src-tauri && cargo test`, `pnpm check`.
- `pre-push` (parallel): `cargo clippy ... -D warnings`, `pnpm audit --audit-level=high || true`, `cargo audit ... || true`.
- `package.json` script `prepare` runs `lefthook install`.

## Related
- [Build and Package](./build-and-package.md)
- [Testing](../crosscutting/testing.md)
