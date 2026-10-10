---
id: crosscutting/state-management
schema: okf/schemas/v1/architecture.json
type: Architecture
title: State Management
description: Where run-time state lives in each process.
domain: architecture
tags:
  - crosscutting
  - state
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/lib/state.svelte.ts
  - resource: src/lib/library.svelte.ts
  - resource: src/lib/blobStore.ts
  - resource: src-tauri/src/sidecar.rs
  - resource: src-tauri/sidecar/server.py
relations:
  relates_to:
    - building-blocks/frontend-state-and-ipc
    - runtime/sidecar-startup
    - crosscutting/configuration
---
# State Management

Each process keeps its state in module-level or managed objects; durable state is on disk.

## Facts

- Webview: `appState` and `libraryState` are Svelte 5 `$state` objects; `RecordingState` has nine values from `ready` to `saved` (`src/lib/state.svelte.ts`).
- Webview: `blobStore` holds the browser-mode video and audio blobs (`src/lib/blobStore.ts`).
- Rust: `SidecarState` is Tauri managed state with the child, port, data dir, `starting` and a `Notify` (`src-tauri/src/sidecar.rs`).
- Rust: `HttpClient` is managed state (`src-tauri/src/local_tts.rs`).
- Sidecar: `_generations` (dict), `_generation_queue`, `_vc_model`, `_model_cache` with a 30 second TTL (`src-tauri/sidecar/server.py`); `_qwen_model` and `_whisper_model` in `src-tauri/sidecar/tts.py`.
- Disk: `config.json`, `profiles/`, `models/`, `generations/`, `cache/` under the app data dir; recordings in the output dir with `.meta.json` files.

## Related

- [Frontend State and IPC](../building-blocks/frontend-state-and-ipc.md)
- [Flow: Sidecar Startup and Health](../runtime/sidecar-startup.md)
- [Configuration](configuration.md)
