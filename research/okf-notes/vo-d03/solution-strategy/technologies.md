---
id: solution-strategy/technologies
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Technologies and structural decisions"
description: "Languages, frameworks and the process split between webview and Rust backend."
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
  - resource: src/lib/state.svelte.ts
relations:
  relates_to:
    - context/system-context
    - building-blocks/frontend-shell
    - building-blocks/backend-entry
---

# Technologies and structural decisions

The app is a SvelteKit single-page frontend inside a Tauri 2 webview, with a Rust library crate as the backend process.

## Technologies

| Technology | Shown by |
|---|---|
| Svelte 5 with runes (`$state`, `$derived`, `$props`) | `package.json` (`svelte`), `svelte.config.js` (`runes: true`), `src/lib/state.svelte.ts` |
| SvelteKit 2, static adapter with `fallback: 'index.html'` | `package.json`, `svelte.config.js` |
| TypeScript, `strict: true` | `tsconfig.json` |
| Vite 7, dev port 5170 | `vite.config.ts` |
| Tauri 2 with plugins shell, dialog, fs, log, global-shortcut | `src-tauri/Cargo.toml`, `src-tauri/src/lib.rs` |
| Rust 2021, `reqwest`, `tokio`, `serde`, `sha2`, `base64`, `rand`, `url`, `open`, `dirs` | `src-tauri/Cargo.toml` |
| ffmpeg CLI (desktop) and `@ffmpeg/ffmpeg` wasm (browser) | `src-tauri/src/ffmpeg.rs`, `package.json` |
| pnpm, run by Tauri before dev and build | `src-tauri/tauri.conf.json` |

## Structural decisions visible in code

- Prerendered client-only pages: `export const ssr = false; export const prerender = true;` (`src/routes/+layout.ts`).
- Two execution modes. `isTauri()` in `src/lib/state.svelte.ts` tests `window.__TAURI_INTERNALS__`; each page branches on it between `invoke` calls and direct browser APIs.
- Heavy work (ffmpeg, ElevenLabs upload, Drive OAuth) lives in Rust commands in desktop mode.
- Progress travels over Tauri `Channel` objects (`src-tauri/src/pipeline.rs`).
- Config is stored in the app data directory by Rust and in `localStorage` by the frontend.

## Related

- [context/system-context](../context/system-context.md)
- [building-blocks/frontend-shell](../building-blocks/frontend-shell.md)
- [building-blocks/backend-entry](../building-blocks/backend-entry.md)
- [runtime/process-recording-desktop](../runtime/process-recording-desktop.md)
- [runtime/process-recording-browser](../runtime/process-recording-browser.md)
