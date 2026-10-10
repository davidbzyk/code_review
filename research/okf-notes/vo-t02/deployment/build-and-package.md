---
id: deployment/build-and-package
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Build and Package"
description: "Build commands, packaging config and outputs as the project files state them."
domain: architecture
tags:
  - deployment
  - build
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: package.json
  - resource: docs/BUILD.md
  - resource: src-tauri/tauri.conf.json
  - resource: src-tauri/Cargo.toml
  - resource: src-tauri/build.rs
  - resource: svelte.config.js
  - resource: vite.config.ts
  - resource: src-tauri/Info.plist
  - resource: src-tauri/capabilities/default.json
  - resource: scripts/generate-icon.py
related:
  - deployment/ci-and-hooks
  - crosscutting/security-boundaries
  - building-blocks/icon-tooling
---
# Build and Package

The app builds as a static SvelteKit site wrapped by Tauri into a macOS bundle.

## Commands
- `pnpm install`, `pnpm dev` (`vite dev`), `pnpm build` (`vite build`), `pnpm check` (package.json).
- `pnpm tauri dev` and `pnpm tauri build` (docs/BUILD.md).
- `pnpm test`, `pnpm test:rust` (`cd src-tauri && cargo test`), `pnpm test:all` (package.json).

## Packaging config (src-tauri/tauri.conf.json)
- `frontendDist` is `../build`; `devUrl` is `http://localhost:5170`.
- `beforeDevCommand` is `pnpm dev`; `beforeBuildCommand` is `pnpm build`.
- `bundle.targets` is `all`; `externalBin` is `binaries/ffmpeg`.
- Identifier `com.voiceover.app`, product name `VoiceOver`, version `0.1.0`.
- Crate types `staticlib`, `cdylib`, `rlib`, library name `voiceover_lib` (src-tauri/Cargo.toml).

## Outputs (docs/BUILD.md)
`VoiceOver.app` under `src-tauri/target/release/bundle/macos/` and a `.dmg` under `.../bundle/dmg/`. The doc places the ffmpeg binary at `src-tauri/binaries/ffmpeg-<target triple>`.

## Build-time steps
`vite.config.ts` plugin `stripConfigPlugin` removes `build/_config.json` on `closeBundle`. `src-tauri/build.rs` runs `tauri_build::build()`. The capability file src-tauri/capabilities/default.json lists permissions for windows `main` and `widget`.

## Related
- [CI and Git Hooks](./ci-and-hooks.md)
- [Security Boundaries](../crosscutting/security-boundaries.md)
- [Icon Tooling](../building-blocks/icon-tooling.md)
