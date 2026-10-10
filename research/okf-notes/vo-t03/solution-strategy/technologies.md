---
id: solution-strategy/technologies
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Technologies and structural decisions"
description: "Languages, frameworks and the process split visible in the manifests and code."
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
  - resource: src-tauri/tauri.conf.json
  - resource: src-tauri/sidecar/requirements.txt
  - resource: svelte.config.js
  - resource: vite.config.ts
  - resource: src-tauri/src/lib.rs
related:
  - context/system-context
  - deployment/build-and-run
  - crosscutting/configuration
---
# Technologies and structural decisions

The app is three layers in three processes: a SvelteKit webview, a Rust Tauri host, and a Python sidecar.

## Technologies

| Technology | Evidence |
|---|---|
| Svelte 5 with runes, SvelteKit 2, adapter-static with `fallback: 'index.html'` | package.json, svelte.config.js |
| Vite dev server on port 5170 (`strictPort`) | vite.config.ts |
| TypeScript, vitest with jsdom | package.json |
| `@ffmpeg/ffmpeg` (wasm) for browser mode | package.json, src/routes/preview/+page.svelte |
| Tauri 2 with shell, dialog, fs, log, global-shortcut plugins | src-tauri/Cargo.toml, src-tauri/src/lib.rs |
| Rust 2021, tokio, reqwest, serde | src-tauri/Cargo.toml |
| `keyring` (apple-native, linux-native) for secrets | src-tauri/Cargo.toml |
| FastAPI, uvicorn | src-tauri/sidecar/requirements.txt |
| MLX, mlx-whisper, mlx-audio, qwen-tts, torch, transformers | src-tauri/sidecar/requirements.txt |
| yt-dlp | src-tauri/sidecar/requirements.txt |
| PyInstaller (spec file) | src-tauri/sidecar/voiceover-tts.spec |

## Structural decisions

- The frontend is prerendered with `ssr = false` (src/routes/+layout.ts).
- Every Tauri call goes through `tauriInvoke` (src/lib/tauri.ts).
- The same page code has a Tauri branch and a browser branch, chosen by `isTauri()` (src/lib/state.svelte.ts, src/routes/preview/+page.svelte).
- Video processing runs in ffmpeg started from Rust (src-tauri/src/ffmpeg.rs).
- Local TTS runs in a separate process reached over loopback HTTP; the host picks a free port and passes `--parent-pid` so the sidecar exits with its parent (src-tauri/src/sidecar.rs, src-tauri/sidecar/server.py).
- Secrets live in the OS keychain, not in `config.json` (src-tauri/src/secrets.rs).
- Progress is pushed from Rust to the page through Tauri `Channel` objects (src-tauri/src/pipeline.rs).

## Related

- [[context/system-context]]
- [[deployment/build-and-run]]
- [[crosscutting/configuration]]
