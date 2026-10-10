---
id: deployment/build-and-packaging
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Build, packaging and start
description: Scripts, bundler config and capability files that build and start the desktop app.
domain: architecture
tags:
  - deployment
  - arc42-7
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: package.json
  - resource: svelte.config.js
  - resource: vite.config.ts
  - resource: src-tauri/tauri.conf.json
  - resource: src-tauri/Cargo.toml
  - resource: src-tauri/build.rs
  - resource: src-tauri/capabilities/default.json
  - resource: src-tauri/.gitignore
  - resource: .gitignore
  - resource: .npmrc
  - resource: tsconfig.json
related:
  - solution-strategy/technology-choices
  - context/system-context
  - crosscutting/security-permissions
---

The frontend builds with Vite into `build/`, and Tauri bundles that directory with the Rust library.

## Scripts (package.json)
`dev` = `vite dev`; `build` = `vite build`; `preview` = `vite preview`; `prepare` = `svelte-kit sync || echo ''`; `check` and `check:watch` run `svelte-kit sync` and `svelte-check --tsconfig ./tsconfig.json`.

## Tauri (src-tauri/tauri.conf.json)
- `frontendDist`: `../build`; `devUrl`: `http://localhost:5170`.
- `beforeDevCommand`: `pnpm dev`; `beforeBuildCommand`: `pnpm build`.
- `bundle.active` true, `targets` `all`, icons under `icons/`.
- Identifier `com.voiceover.app`, version 0.1.0.

## Build outputs
- `adapter-static` with fallback `index.html` writes the static site (svelte.config.js).
- Cargo builds `voiceover_lib` as staticlib, cdylib and rlib; `build.rs` runs `tauri_build::build()` (src-tauri/Cargo.toml).
- `.gitignore` lists `node_modules`, `/build`, `/.svelte-kit`.

## Start
`tauri dev` and `tauri build` come from `@tauri-apps/cli` in package.json; the process starts at `main()` in src-tauri/src/main.rs.

## Capabilities
src-tauri/capabilities/default.json grants window, shell, dialog, fs and global-shortcut permissions to windows `main` and `widget`.

## Related
[[solution-strategy/technology-choices]], [[context/system-context]], [[crosscutting/security-permissions]]
