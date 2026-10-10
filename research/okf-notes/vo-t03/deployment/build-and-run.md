---
id: deployment/build-and-run
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Build, dev and test commands"
description: "Scripts and config that build, run and test the app."
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
  - resource: vite.config.ts
  - resource: svelte.config.js
  - resource: src-tauri/Cargo.toml
  - resource: src-tauri/Info.plist
  - resource: src-tauri/build.rs
  - resource: vitest.config.ts
related:
  - deployment/sidecar-packaging
  - deployment/quality-gates
  - solution-strategy/technologies
---
# Build, dev and test commands

The frontend is built by Vite and wrapped by Tauri; Cargo builds the host.

## Commands (package.json)

- `dev`: `vite dev`; `build`: `vite build`; `preview`: `vite preview`.
- `check`: `svelte-kit sync && svelte-check --tsconfig ./tsconfig.json`.
- `test`: `vitest run`; `test:rust`: `cd src-tauri && cargo test`; `test:all` runs both.
- `prepare`: `lefthook install`.

## Tauri config (src-tauri/tauri.conf.json)

- `beforeDevCommand`: `pnpm dev`; `devUrl`: `http://localhost:5170`.
- `beforeBuildCommand`: `pnpm build`; `frontendDist`: `../build`.
- Main window `main`, 480 by 640, product name `VoiceOver`, identifier `com.voiceover.app`.
- `bundle.externalBin`: `binaries/ffmpeg` and `binaries/voiceover-tts`; `targets`: `all`.

## Other files

- `vite.config.ts` has a plugin `stripConfigPlugin` that deletes `build/_config.json` on `closeBundle`.
- `Cargo.toml` builds `staticlib`, `cdylib` and `rlib` crate types, and excludes `sidecar/` from cargo's file set.
- `Info.plist` has camera, microphone and screen capture usage strings.
- `vitest.config.ts` uses jsdom and v8 coverage thresholds for `src/lib`.

## Related

- [[deployment/sidecar-packaging]]
- [[deployment/quality-gates]]
- [[solution-strategy/technologies]]
