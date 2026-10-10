---
id: deployment/build-and-package
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Build, package and start"
description: "Scripts and config that build the frontend, bundle the Tauri app and run it."
domain: architecture
tags:
  - deployment
  - build
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
architecture_layer: deployment
sources:
  - resource: package.json
  - resource: src-tauri/tauri.conf.json
  - resource: src-tauri/Cargo.toml
  - resource: svelte.config.js
  - resource: vite.config.ts
  - resource: src-tauri/build.rs
  - resource: src-tauri/Info.plist
  - resource: src-tauri/capabilities/default.json
  - resource: .npmrc
related:
  - solution-strategy/technologies
  - building-blocks/backend-shell
  - interfaces/tauri-capabilities
---

# Build, package and start

The frontend builds to static files in `build/`, and Tauri bundles them with the Rust library.

## Scripts (package.json)
- `dev`: `vite dev`; `build`: `vite build`; `preview`: `vite preview`.
- `prepare`: `svelte-kit sync`; `check`: `svelte-kit sync && svelte-check --tsconfig ./tsconfig.json`.
- `@tauri-apps/cli` is a dev dependency.

## Tauri config (src-tauri/tauri.conf.json)
- `beforeDevCommand` `pnpm dev`; `beforeBuildCommand` `pnpm build`.
- `devUrl` `http://localhost:5170`; `frontendDist` `../build`.
- `bundle.active` true, `targets` `all`, icons listed under `icons/`.
- `identifier` `com.voiceover.app`; CSP `connect-src` lists the ElevenLabs and Google hosts.

## Rust and packaging
- Library `voiceover_lib`, crate types `staticlib`, `cdylib`, `rlib` (src-tauri/Cargo.toml).
- `build.rs` runs `tauri_build::build()`.
- `Info.plist` holds camera, microphone and screen capture usage strings.
- `.npmrc` sets `engine-strict=true`.

## Related

- [[solution-strategy/technologies]]
- [[building-blocks/backend-shell]]
- [[interfaces/tauri-capabilities]]
