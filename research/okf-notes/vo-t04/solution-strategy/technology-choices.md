---
id: solution-strategy/technology-choices
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Technology choices"
description: "The app pairs a SvelteKit static frontend with a Rust Tauri backend and runs the same flows in a webview or in a plain browser."
domain: architecture
tags:
  - strategy
  - technology
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: package.json
  - resource: src-tauri/Cargo.toml
  - resource: svelte.config.js
  - resource: vite.config.ts
  - resource: vitest.config.ts
  - resource: tsconfig.json
  - resource: src-tauri/tauri.conf.json
  - resource: lefthook.yml
  - resource: src/routes/+layout.ts
relations:
  relates_to:
    - context/system-context
    - deployment/build-and-package
    - crosscutting/state-management
---
# Technology choices

The code splits into a TypeScript/Svelte frontend and a Rust backend, and the frontend branches on `isTauri()` to run a browser-only path.

## Technologies

| Technology | Evidence |
|---|---|
| SvelteKit 2, Svelte 5 (runes: `$state`, `$derived`, `$props`) | package.json, svelte.config.js |
| `@sveltejs/adapter-static` with `fallback: 'index.html'` | svelte.config.js |
| Client-only rendering: `ssr = false`, `prerender = true` | src/routes/+layout.ts, src/routes/widget/+layout.ts |
| Vite 7, dev port 5170 with `strictPort` | package.json, vite.config.ts |
| TypeScript, strict mode | tsconfig.json |
| Tauri 2 desktop shell | src-tauri/Cargo.toml, src-tauri/tauri.conf.json |
| Rust 2021 edition, `rust-version = "1.77.2"` | src-tauri/Cargo.toml |
| tokio, reqwest (multipart, json, stream), serde | src-tauri/Cargo.toml |
| `@ffmpeg/ffmpeg` (wasm) for the browser path | package.json, src/routes/preview/+page.svelte |
| Vitest with jsdom, v8 coverage | vitest.config.ts |
| lefthook pre-commit | lefthook.yml |

## Structural decisions

- Two execution paths in one codebase: Tauri commands in Rust, or `fetch` and ffmpeg.wasm in the page (src/routes/preview/+page.svelte).
- Backend commands are registered in one `generate_handler!` list (src-tauri/src/lib.rs).
- The Rust crate builds as `staticlib`, `cdylib` and `rlib` under the name `voiceover_lib` (src-tauri/Cargo.toml).
- Configuration is kept in Tauri app data, `localStorage` and a synced static file (see [[crosscutting/configuration]]).

## Related

[[context/system-context]], [[deployment/build-and-package]], [[crosscutting/state-management]]
