---
id: solution-strategy/technology-choices
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Technology choices
description: Languages, frameworks and the structural split between web frontend and Rust backend.
domain: architecture
tags:
  - strategy
  - arc42-4
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: package.json
  - resource: src-tauri/Cargo.toml
  - resource: svelte.config.js
  - resource: vite.config.ts
  - resource: tsconfig.json
  - resource: src-tauri/tauri.conf.json
  - resource: src/routes/+layout.ts
  - resource: .npmrc
related:
  - context/system-context
  - deployment/build-and-packaging
  - crosscutting/state-management
---

The app is a SvelteKit static frontend running inside a Tauri 2 shell with a Rust library as backend, and the same frontend also runs in a plain browser.

## Technologies
| Technology | Shown by |
|---|---|
| TypeScript, strict mode | tsconfig.json |
| Svelte 5 with runes (`$state`, `$derived`, `$props`) | package.json, svelte.config.js (`runes: true` for non-node_modules files) |
| SvelteKit 2 with `adapter-static`, fallback `index.html` | svelte.config.js |
| Vite 7, port 5170, strict port | vite.config.ts |
| Tauri 2 (`tauri`, `@tauri-apps/api`, `@tauri-apps/cli`) | package.json, src-tauri/Cargo.toml |
| Rust edition 2021, crate `voiceover_lib` (staticlib, cdylib, rlib) | src-tauri/Cargo.toml |
| tokio, reqwest (multipart, json, stream) | src-tauri/Cargo.toml |
| Tauri plugins: shell, dialog, fs, global-shortcut, log | src-tauri/Cargo.toml |
| ffmpeg.wasm (`@ffmpeg/ffmpeg`, `@ffmpeg/util`, `@ffmpeg/core` 0.12.10) | package.json |
| pnpm commands in Tauri build hooks; `engine-strict=true` | src-tauri/tauri.conf.json, .npmrc |

## Structural decisions
- Pages are prerendered with SSR off: `export const ssr = false; export const prerender = true;` (src/routes/+layout.ts, src/routes/widget/+layout.ts).
- Every page checks `isTauri()` and takes a Rust path (`invoke`) or a browser path (`fetch`, MediaRecorder blobs, ffmpeg.wasm) (src/lib/state.svelte.ts).
- Media processing in the desktop app is done by the system `ffmpeg` binary in Rust; in browser mode by ffmpeg.wasm.
- Two windows share one frontend bundle: `main` and `widget` (routes `/` and `/widget`).
- Cross-window messages use Tauri events (`recording-stop`, `recording-cancel`).

## Related
[[context/system-context]], [[deployment/build-and-packaging]], [[crosscutting/state-management]]
