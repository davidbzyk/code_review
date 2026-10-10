---
id: deployment/quality-gates
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Hooks, CI and icon generation"
description: "Git hooks, the CI workflow and the icon generator script."
domain: architecture
tags:
  - deployment
  - ci
  - tooling
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: lefthook.yml
  - resource: scripts/generate-icon.py
  - resource: pnpm-workspace.yaml
related:
  - deployment/build-and-run
  - crosscutting/testing
---
# Hooks, CI and icon generation

Quality checks run from lefthook locally and from one GitHub Actions workflow.

## lefthook.yml

- `pre-commit` (parallel): `pnpm test`, `cd src-tauri && cargo test`, `pnpm check`.
- `pre-push` (parallel): `cargo clippy --manifest-path src-tauri/Cargo.toml -- -D warnings`, `pnpm audit --audit-level=high || true`, `cargo audit --file src-tauri/Cargo.lock`.

## .github/workflows/ci.yml

- Runs on push and pull request to `main`.
- Job `frontend` on ubuntu-latest: `pnpm install --frozen-lockfile`, `pnpm check`, `pnpm test`, `pnpm audit`.
- Job `rust` on macos-latest: creates empty sidecar placeholder files under `src-tauri/binaries`, then runs clippy, `cargo test` and `cargo audit`.

## scripts/generate-icon.py

- `draw_microphone(size)` draws the icon with Pillow; `main()` writes PNG sizes, `icon.ico`, and `icon.icns` through `iconutil`, into `src-tauri/icons`.

## pnpm-workspace.yaml

- `allowBuilds` with `esbuild: true`.

## Related

- [[deployment/build-and-run]]
- [[crosscutting/testing]]
