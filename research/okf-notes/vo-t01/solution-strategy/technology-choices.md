---
id: solution-strategy/technology-choices
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Technology Choices
description: Languages, frameworks and structural decisions visible in the manifests and code.
domain: architecture
tags:
  - strategy
  - arc42
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: package.json
  - resource: src-tauri/Cargo.toml
  - resource: src-tauri/sidecar/requirements.txt
  - resource: svelte.config.js
  - resource: vite.config.ts
  - resource: vitest.config.ts
  - resource: src-tauri/tauri.conf.json
  - resource: src/routes/+layout.ts
  - resource: src-tauri/capabilities/default.json
relations:
  relates_to:
    - context/system-context
    - building-blocks/rust-app-shell
    - building-blocks/sidecar-server
    - interfaces/tauri-commands-app
---
# Technology Choices

The app is split into three processes: a Svelte webview, a Rust core, and a Python TTS sidecar.

## Technologies

| Technology | Shown by |
|---|---|
| Tauri 2, Rust edition 2021 | `src-tauri/Cargo.toml` (`tauri = 2.10.3`) |
| SvelteKit 2, Svelte 5 runes | `package.json`, `svelte.config.js` (`runes: true`) |
| adapter-static, fallback `index.html` | `svelte.config.js` |
| Vite dev server on port 5170 | `vite.config.ts`, `src-tauri/tauri.conf.json` |
| Vitest with jsdom | `vitest.config.ts` |
| reqwest, tokio | `src-tauri/Cargo.toml` |
| keyring (apple-native, linux-native) | `src-tauri/Cargo.toml` |
| FastAPI, uvicorn | `src-tauri/sidecar/requirements.txt` |
| mlx, mlx-whisper, mlx-audio, qwen-tts, torch | `src-tauri/sidecar/requirements.txt` |
| yt-dlp | `src-tauri/sidecar/requirements.txt` |
| @ffmpeg/ffmpeg (wasm, browser mode) | `package.json` |

## Structural decisions

- Pages set `ssr = false` and `prerender = true` (`src/routes/+layout.ts`).
- The webview reaches Rust through `invoke` (`src/lib/tauri.ts`); the webview does not call the sidecar directly.
- Rust forwards sidecar calls over HTTP on 127.0.0.1 (`src-tauri/src/local_tts.rs`).
- The Tauri capability file lists permitted window, shell, dialog and fs operations (`src-tauri/capabilities/default.json`).
- Secrets live in the keychain, other settings in `config.json` (`src-tauri/src/config.rs`).

## Related

- [System Context](../context/system-context.md)
- [Rust App Shell](../building-blocks/rust-app-shell.md)
- [Sidecar Server](../building-blocks/sidecar-server.md)
- [Tauri Commands: Config, Recording, Library, Drive, Window](../interfaces/tauri-commands-app.md)
