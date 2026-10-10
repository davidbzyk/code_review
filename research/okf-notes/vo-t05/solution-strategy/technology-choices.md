---
id: solution-strategy/technology-choices
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Technology Choices
description: Languages, frameworks and the process split visible in the manifests and source.
domain: architecture
tags:
  - solution-strategy
  - arc42
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: package.json
  - resource: src-tauri/Cargo.toml
  - resource: src-tauri/tauri.conf.json
  - resource: src-tauri/sidecar/requirements.txt
  - resource: svelte.config.js
  - resource: vite.config.ts
  - resource: tsconfig.json
  - resource: src-tauri/src/lib.rs
related:
  - context/system-context
  - deployment/build-and-packaging
  - building-blocks/rust-sidecar-manager
---

# Technology Choices

The app is three programs: a Svelte web UI in a Tauri webview, a Rust host, and a Python sidecar process.

| Technology | Evidence |
|---|---|
| SvelteKit 2, Svelte 5 runes, static adapter with `fallback: 'index.html'` | package.json, svelte.config.js |
| TypeScript, `ssr = false`, `prerender = true` | src/routes/+layout.ts |
| Vite 7, dev port 5170 with `strictPort` | vite.config.ts |
| Tauri 2 (`tauri` 2.10.3) with shell, dialog, fs, log, global-shortcut plugins | src-tauri/Cargo.toml |
| Rust 2021, `tokio`, `reqwest`, `serde` | src-tauri/Cargo.toml |
| `keyring` for the OS keychain | src-tauri/Cargo.toml, src-tauri/src/secrets.rs |
| FastAPI and uvicorn sidecar | src-tauri/sidecar/requirements.txt, server.py |
| MLX Whisper, `mlx-audio`, `qwen-tts`, `torch` | requirements.txt, tts.py |
| `yt-dlp` | requirements.txt, server.py |
| PyInstaller binary `voiceover-tts` | src-tauri/sidecar/voiceover-tts.spec |
| ffmpeg bundled as `binaries/ffmpeg`; `@ffmpeg/ffmpeg` 0.12 in the browser | src-tauri/tauri.conf.json, package.json |
| Vitest with jsdom | vitest.config.ts |

## Structural decisions

- The webview calls Rust through `invoke`; Rust calls the sidecar over HTTP on `127.0.0.1` with a port chosen at startup (src-tauri/src/sidecar.rs `find_available_port`).
- The frontend reaches the sidecar only through Rust commands `sidecar_fetch` and `sidecar_upload` (src-tauri/src/local_tts.rs).
- Two voice providers, `elevenlabs` and `local` (src-tauri/src/tts_provider.rs `Provider`).
- The frontend also has a browser mode that runs without Tauri: `isTauri()` selects the path (src/lib/state.svelte.ts).
- Secrets live in the keychain, not in `config.json` (src-tauri/src/secrets.rs).

## Related

- [System Context](../context/system-context.md)
- [Build and Packaging](../deployment/build-and-packaging.md)
- [Rust Sidecar Manager](../building-blocks/rust-sidecar-manager.md)
