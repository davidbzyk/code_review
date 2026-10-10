---
id: deployment/ci-and-hooks
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "CI and Git Hooks"
description: "The GitHub Actions workflow and lefthook commands that run checks."
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
relations:
  relates_to:
    - deployment/build-and-package
    - crosscutting/testing
---

Checks run in GitHub Actions on pushes and pull requests to `main`, and locally through lefthook.

## CI jobs (`.github/workflows/ci.yml`)

- `frontend` on `ubuntu-latest`: pnpm 10, Node 22, `pnpm install --frozen-lockfile`, `pnpm check`, `pnpm test`, `pnpm audit --audit-level=high` with `continue-on-error: true`.
- `rust` on `macos-latest`: stable toolchain with clippy, `Swatinem/rust-cache`, creates an empty placeholder file `src-tauri/binaries/ffmpeg-aarch64-apple-darwin`, then `cargo clippy -- -D warnings`, `cargo test`, `cargo install cargo-audit`, `cargo audit --file src-tauri/Cargo.lock`.

## Hooks (`lefthook.yml`)

- `pre-commit` (parallel): `pnpm test`, `cd src-tauri && cargo test`, `pnpm check`.
- `pre-push` (parallel): `cargo clippy` with `-D warnings`, `pnpm audit` and `cargo audit`, the last two ending in `|| true`.
- `package.json` runs `lefthook install` in the `prepare` script.

## Related

- [Build and package](build-and-package.md)
- [Testing](../crosscutting/testing.md)
