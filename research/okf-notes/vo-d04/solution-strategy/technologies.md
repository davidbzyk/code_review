---
id: solution-strategy/technologies
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Technologies and structural decisions"
description: "Languages, frameworks and the frontend/backend process split visible in the manifests."
domain: architecture
tags:
  - strategy
  - technology
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
architecture_layer: solution-strategy
sources:
  - resource: package.json
  - resource: src-tauri/Cargo.toml
  - resource: svelte.config.js
  - resource: vite.config.ts
  - resource: tsconfig.json
  - resource: src-tauri/tauri.conf.json
  - resource: src/routes/+layout.ts
  - resource: src/lib/state.svelte.ts
related:
  - context/system-context
  - deployment/build-and-package
  - crosscutting/state
---

# Technologies and structural decisions

The app is a Tauri 2 desktop shell in Rust that hosts a statically built SvelteKit 5 frontend in TypeScript.

## Technologies
| Technology | Evidence |
|---|---|
| Svelte 5 with runes, SvelteKit 2 | package.json; svelte.config.js (`runes: true`) |
| adapter-static, fallback `index.html` | svelte.config.js |
| Vite 7, dev port 5170 | package.json; vite.config.ts |
| TypeScript, `strict` | tsconfig.json |
| Tauri 2, Rust edition 2021 | src-tauri/Cargo.toml |
| tokio, reqwest (multipart, json, stream) | src-tauri/Cargo.toml |
| Tauri plugins shell, dialog, fs, log, global-shortcut | src-tauri/Cargo.toml; src-tauri/src/lib.rs |
| @ffmpeg/ffmpeg 0.12 (wasm) | package.json |
| sha2, base64, rand, url, open (OAuth PKCE) | src-tauri/Cargo.toml; src-tauri/src/google_drive.rs |

## Structural decisions
- Two processes: a webview running the frontend and a Rust process exposing commands via `invoke_handler` (src-tauri/src/lib.rs).
- Client-only rendering: `ssr = false` and `prerender = true` (src/routes/+layout.ts).
- Two execution modes in one frontend: `isTauri()` selects Tauri commands, otherwise browser APIs, fetch and ffmpeg.wasm (src/lib/state.svelte.ts).
- One shared runes state object, `appState` (src/lib/state.svelte.ts).
- Media processing in desktop mode is done by the system `ffmpeg` program (src-tauri/src/ffmpeg.rs).

## Related

- [[context/system-context]]
- [[deployment/build-and-package]]
- [[crosscutting/state]]
