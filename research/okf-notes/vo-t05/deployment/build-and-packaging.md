---
id: deployment/build-and-packaging
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Build and Packaging
description: Scripts, config and bundle settings that build and package the desktop app.
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
  - resource: src-tauri/Info.plist
  - resource: scripts/generate-icon.py
  - resource: docs/BUILD.md
related:
  - deployment/sidecar-build
  - deployment/ci-and-hooks
  - solution-strategy/technology-choices
---

# Build and Packaging

Tauri builds the web UI and the Rust crate into one bundle.

## Facts

- `pnpm build` runs `vite build`; output goes to `build/` (adapter-static, fallback `index.html`) (package.json, svelte.config.js).
- `tauri.conf.json`: `beforeDevCommand` `pnpm dev`, `beforeBuildCommand` `pnpm build`, `frontendDist` `../build`, `devUrl` `http://localhost:5170`.
- Bundle: `active: true`, `targets: "all"`, icon files, `externalBin` `binaries/ffmpeg` and `binaries/voiceover-tts`.
- The Rust crate `voiceover` has `crate-type = ["staticlib", "cdylib", "rlib"]` and excludes `sidecar/` from cargo's watcher (src-tauri/Cargo.toml).
- `stripConfigPlugin` in vite.config.ts deletes `build/_config.json` after the bundle closes.
- `Info.plist` declares camera, microphone and screen-capture usage strings.
- `scripts/generate-icon.py` draws a microphone icon with PIL into `src-tauri/icons` (`draw_microphone`, `main`).
- `package.json` scripts: `dev`, `build`, `preview`, `check`, `test`, `test:rust`, `test:all`, coverage variants.
- The CSP and window settings are in `tauri.conf.json` (`app.security.csp`).
- docs/BUILD.md lists the manual steps, including downloading a static ffmpeg into `src-tauri/binaries`.

## Related

- [Sidecar Build](./sidecar-build.md)
- [CI and Git Hooks](./ci-and-hooks.md)
- [Technology Choices](../solution-strategy/technology-choices.md)
