---
id: deployment/build-and-package
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Build and package"
description: "pnpm scripts build the static frontend, Tauri bundles it with the Rust binary and an ffmpeg sidecar, and docs/BUILD.md lists the steps."
domain: architecture
tags:
  - deployment
  - build
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: package.json
  - resource: src-tauri/tauri.conf.json
  - resource: src-tauri/Cargo.toml
  - resource: docs/BUILD.md
  - resource: lefthook.yml
  - resource: svelte.config.js
  - resource: vite.config.ts
  - resource: src-tauri/.gitignore
  - resource: src-tauri/Info.plist
relations:
  relates_to:
    - solution-strategy/technology-choices
    - crosscutting/testing
    - context/system-context
---
# Build and package

Build and start commands are defined in package.json and src-tauri/tauri.conf.json, and described in docs/BUILD.md.

## Commands

- `pnpm dev` runs `vite dev` on port 5170; `pnpm build` runs `vite build` (package.json).
- `pnpm tauri dev` (docs/BUILD.md); the config sets `beforeDevCommand: pnpm dev` and `devUrl: http://localhost:5170`.
- `pnpm tauri build`: `beforeBuildCommand: pnpm build`, `frontendDist: ../build` (src-tauri/tauri.conf.json).
- `pnpm check` runs `svelte-kit sync && svelte-check`; `prepare` runs `lefthook install`.
- Tests: `pnpm test`, `pnpm test:rust`, `pnpm test:all` (package.json).

## Packaging

- `bundle.targets` is `all`, with icons listed and `externalBin: ["binaries/ffmpeg"]` (src-tauri/tauri.conf.json).
- docs/BUILD.md names the artifacts `src-tauri/target/release/bundle/macos/VoiceOver.app` and a `.dmg` under `bundle/dmg`, and says to place the ffmpeg binary as `src-tauri/binaries/ffmpeg-<arch>-apple-darwin`.
- The crate library types are `staticlib`, `cdylib`, `rlib` (src-tauri/Cargo.toml).
- src-tauri/Info.plist carries camera, microphone and screen capture usage strings.
- src-tauri/.gitignore lists `/target/` and `/gen/schemas`.
- The frontend uses `adapter-static` with `fallback: 'index.html'` (svelte.config.js); a Vite plugin deletes `build/_config.json` (vite.config.ts).
- lefthook.yml runs `pnpm test`, `cargo test` and `pnpm check` on pre-commit.

## Related

[[solution-strategy/technology-choices]], [[crosscutting/testing]], [[context/system-context]]
