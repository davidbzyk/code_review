---
id: solution-strategy/technologies
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Technologies and structural decisions
description: The code combines a SvelteKit web UI, a Rust Tauri host and a Python FastAPI sidecar in three cooperating processes.
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
  - resource: src-tauri/sidecar/requirements.txt
  - resource: svelte.config.js
  - resource: vite.config.ts
  - resource: src-tauri/tauri.conf.json
  - resource: tsconfig.json
related:
  - context/system-context
  - deployment/build-and-packaging
  - interfaces/tauri-commands
  - interfaces/sidecar-http-routes
---

# Technologies and structural decisions

The application is split into a web UI, a Rust host process and a Python sidecar process that talk over Tauri IPC and loopback HTTP.

## Technologies

| Technology | Evidence |
|---|---|
| Svelte 5 runes, SvelteKit 2 | package.json (`svelte`, `@sveltejs/kit`), svelte.config.js (`runes: true`) |
| Static adapter, SPA fallback `index.html` | svelte.config.js (`adapter-static`) |
| Vite 7 dev server on port 5170 | vite.config.ts, src-tauri/tauri.conf.json (`devUrl`) |
| TypeScript, strict | tsconfig.json |
| Tauri 2 with shell, dialog, fs, log, global-shortcut plugins | src-tauri/Cargo.toml |
| Rust, tokio, reqwest, serde | src-tauri/Cargo.toml |
| OS keychain (`keyring`) | src-tauri/Cargo.toml, src-tauri/src/secrets.rs |
| ffmpeg.wasm in browser mode | package.json (`@ffmpeg/ffmpeg`), src/routes/preview/+page.svelte |
| FastAPI and uvicorn | src-tauri/sidecar/requirements.txt, src-tauri/sidecar/server.py |
| MLX Whisper, MLX Audio, Qwen TTS, torch | src-tauri/sidecar/requirements.txt, src-tauri/sidecar/tts.py |
| yt-dlp | src-tauri/sidecar/requirements.txt |
| PyInstaller | src-tauri/sidecar/voiceover-tts.spec |

## Structural decisions

- The UI is client-only: `ssr = false` in the layouts (src/routes/+layout.ts, src/routes/widget/+layout.ts).
- Two modes share one UI: Tauri mode uses `invoke` commands, browser mode uses `fetch` and `MediaRecorder` blobs (src/lib/state.svelte.ts `isTauri`, src/lib/recorder.svelte.ts).
- Two voice providers: `elevenlabs` (cloud) and `local` (sidecar), chosen by `AppConfig.provider` (src-tauri/src/config.rs).
- The sidecar binds a random free port and exits when its parent process disappears (src-tauri/src/sidecar.rs, src-tauri/sidecar/server.py `_start_parent_watchdog`).

## Related

- [[context/system-context]] - System context
- [[deployment/build-and-packaging]] - Build and packaging
- [[interfaces/tauri-commands]] - Tauri commands
- [[interfaces/sidecar-http-routes]] - Sidecar HTTP routes
