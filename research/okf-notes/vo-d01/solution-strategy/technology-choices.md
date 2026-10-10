---
id: solution-strategy/technology-choices
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Technology Choices"
description: "Languages, frameworks and the process split between the Rust backend and the Svelte frontend."
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
  - resource: tsconfig.json
  - resource: src-tauri/tauri.conf.json
  - resource: src-tauri/capabilities/default.json
---
# Technology Choices

The application is a Tauri 2 shell with a Rust backend and a statically built SvelteKit frontend that also runs in a plain browser.

## Technologies
| Technology | Shown in |
|---|---|
| Svelte 5 with runes (`$state`, `$derived`, `$props`) | package.json, svelte.config.js |
| SvelteKit 2 with `adapter-static`, fallback `index.html` | svelte.config.js |
| Vite 7, dev port 5170 with `strictPort` | vite.config.ts, package.json |
| TypeScript, `strict: true` | tsconfig.json |
| Tauri 2.10 with shell, dialog, fs, log, global-shortcut plugins | src-tauri/Cargo.toml |
| reqwest 0.12 (multipart, json, stream), tokio | src-tauri/Cargo.toml |
| sha2, base64, rand, url, open for the OAuth PKCE flow | src-tauri/Cargo.toml |
| `@ffmpeg/ffmpeg` 0.12 (wasm) | package.json |

## Structural decisions
- Process split: Rust commands do file, ffmpeg and network work; the frontend calls them with `invoke` (src-tauri/src/lib.rs, src/routes/preview/+page.svelte).
- Dual mode: each frontend module tests `__TAURI_INTERNALS__` through `isTauri()` and falls back to browser APIs (src/lib/state.svelte.ts, src/lib/recorder.svelte.ts).
- Prerendered static pages with SSR off (src/routes/+layout.ts).
- Window permissions are declared in capabilities (src-tauri/capabilities/default.json).

## Related
- [[context/system-context]]
- [[deployment/build-and-packaging]]
- [[crosscutting/dual-runtime-mode]]
