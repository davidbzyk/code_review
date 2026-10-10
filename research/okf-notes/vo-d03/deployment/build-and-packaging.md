---
id: deployment/build-and-packaging
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Build, packaging and start"
description: "Scripts and config files that build the frontend, bundle the Tauri app and start it."
domain: architecture
tags:
  - deployment
  - build
  - arc42-7
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
  - resource: src-tauri/Info.plist
  - resource: src-tauri/.gitignore
  - resource: .gitignore
  - resource: .npmrc
relations:
  relates_to:
    - solution-strategy/technologies
    - building-blocks/backend-entry
---

# Build, packaging and start

The app is built with pnpm and Vite for the frontend and Cargo through the Tauri CLI for the desktop bundle.

## Scripts (`package.json`)

`dev` is `vite dev`; `build` is `vite build`; `preview` is `vite preview`; `prepare` is `svelte-kit sync || echo ''`; `check` and `check:watch` run `svelte-kit sync` then `svelte-check --tsconfig ./tsconfig.json`. `@tauri-apps/cli` is a dev dependency.

## Tauri (`src-tauri/tauri.conf.json`)

- `productName` VoiceOver, `identifier` `com.voiceover.app`, version 0.1.0.
- `build.frontendDist` is `../build`; `devUrl` is `http://localhost:5170`.
- `beforeDevCommand` is `pnpm dev`; `beforeBuildCommand` is `pnpm build`.
- One window `main`, 480 by 640.
- `bundle.active` true, `targets` `all`, icons under `icons/`.

## Output

- `vite build` with `@sveltejs/adapter-static` writes the static site (`fallback: 'index.html'`); `build` is listed in `.gitignore`.
- Cargo builds crate `voiceover` with `crate-type = ["staticlib", "cdylib", "rlib"]` and library `voiceover_lib` (`src-tauri/Cargo.toml`); `build.rs` runs `tauri_build::build()`.
- `src-tauri/Info.plist` holds camera, microphone and screen capture usage strings.
- `.npmrc` sets `engine-strict=true`.

## Related

- [solution-strategy/technologies](../solution-strategy/technologies.md)
- [building-blocks/backend-entry](../building-blocks/backend-entry.md)
- [crosscutting/permissions-and-csp](../crosscutting/permissions-and-csp.md)
