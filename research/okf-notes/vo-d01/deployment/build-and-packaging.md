---
id: deployment/build-and-packaging
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Build and Packaging"
description: "Build scripts, config and bundle settings for the web and desktop builds."
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
  - resource: src-tauri/build.rs
  - resource: svelte.config.js
  - resource: vite.config.ts
  - resource: .npmrc
  - resource: src-tauri/capabilities/default.json
---
# Build and Packaging

The frontend builds to static files in `build`, and Tauri packages them with the Rust crate.

## Facts
- Scripts in package.json: `dev` (`vite dev`), `build` (`vite build`), `preview`, `prepare` (`svelte-kit sync`), `check`, `check:watch`.
- src-tauri/tauri.conf.json: `beforeDevCommand` `pnpm dev`, `beforeBuildCommand` `pnpm build`, `devUrl` `http://localhost:5170`, `frontendDist` `../build`.
- Bundle: `active` true, `targets` `all`, icon files listed under `icons/`; identifier `com.voiceover.app`; main window 480 by 640; `csp` null.
- Crate: name `voiceover`, `[lib]` name `voiceover_lib`, crate types `staticlib`, `cdylib`, `rlib` (src-tauri/Cargo.toml).
- `adapter-static` with fallback `index.html` (svelte.config.js).
- `engine-strict=true` (.npmrc).
- @tauri-apps/cli is a dev dependency, so the Tauri CLI drives the desktop build.

## Related
- [[solution-strategy/technology-choices]]
- [[context/system-context]]
- [[building-blocks/tauri-shell]]
