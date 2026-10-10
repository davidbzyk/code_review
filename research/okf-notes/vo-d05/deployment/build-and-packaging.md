---
id: deployment/build-and-packaging
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Build and packaging
description: How the web UI, Rust app and sidecar binary are built and bundled into the Tauri app.
domain: architecture
tags:
  - deployment
  - build
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: package.json
  - resource: svelte.config.js
  - resource: vite.config.ts
  - resource: src-tauri/tauri.conf.json
  - resource: src-tauri/Cargo.toml
  - resource: src-tauri/sidecar/voiceover-tts.spec
  - resource: scripts/build-sidecar.sh
  - resource: docs/BUILD.md
  - resource: src-tauri/.gitignore
  - resource: .npmrc
  - resource: pnpm-workspace.yaml
related:
  - building-blocks/build-scripts
  - solution-strategy/technologies
  - crosscutting/testing
---

# Build and packaging

The app is built by Tauri, which runs the Vite build and bundles two external binaries.

## Facts

- `pnpm dev` runs `vite dev` on port 5170 with `strictPort`; `pnpm build` runs `vite build` (package.json, vite.config.ts).
- `tauri.conf.json`: `beforeDevCommand` `pnpm dev`, `beforeBuildCommand` `pnpm build`, `frontendDist` `../build`, `devUrl` `http://localhost:5170`, bundle `targets` `all`.
- `bundle.externalBin` lists `binaries/ffmpeg` and `binaries/voiceover-tts`.
- SvelteKit uses `adapter-static` with fallback `index.html` (svelte.config.js).
- `stripConfigPlugin` in vite.config.ts deletes `build/_config.json` after bundling.
- The Rust crate `voiceover` builds `staticlib`, `cdylib`, `rlib` as `voiceover_lib`, and excludes `sidecar/` from cargo (src-tauri/Cargo.toml).
- The sidecar is frozen by PyInstaller from `voiceover-tts.spec` (entry `server.py`, one executable `voiceover-tts`), via `scripts/build-sidecar.sh`, which copies it to `src-tauri/binaries/voiceover-tts-aarch64-apple-darwin`.
- `docs/BUILD.md` describes the macOS-only build steps and places a static ffmpeg in `src-tauri/binaries`.
- `.npmrc` sets `engine-strict=true`; `pnpm-workspace.yaml` allows the `esbuild` build.
- `src-tauri/.gitignore` ignores `/target/` and `/gen/schemas`.

## Related

- Scripts: [[building-blocks/build-scripts]]. Test commands: [[crosscutting/testing]].

## Related

- [[building-blocks/build-scripts]] - Build and tooling scripts
- [[solution-strategy/technologies]] - Technologies and structural decisions
- [[crosscutting/testing]] - Testing
