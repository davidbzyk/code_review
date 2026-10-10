---
id: crosscutting/state
schema: okf/schemas/v1/architecture.json
type: Architecture
title: State and storage
description: Where state lives: Svelte store, module variables, Rust managed state, files in app data, and sidecar memory.
domain: architecture
tags:
  - crosscutting
  - state
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/lib/state.svelte.ts
  - resource: src/lib/blobStore.ts
  - resource: src/lib/recorder.svelte.ts
  - resource: src-tauri/src/sidecar.rs
  - resource: src-tauri/sidecar/server.py
  - resource: src-tauri/sidecar/profiles.py
  - resource: src-tauri/src/models.rs
related:
  - building-blocks/frontend-state
  - building-blocks/sidecar-engine
  - crosscutting/configuration
---

# State and storage

State sits in five places.

## Facts

- UI: the `appState` singleton (Svelte `$state`) and `blobStore` module variables (src/lib/state.svelte.ts, src/lib/blobStore.ts).
- Recorder: module-level variables for streams, recorders, chunks and session id (src/lib/recorder.svelte.ts).
- Rust: `SidecarState` with mutexes for child, port, data dir and `starting` (src-tauri/src/sidecar.rs).
- Disk: `config.json` and `models/` under app data (src-tauri/src/models.rs `get_models_disk_usage`), recordings under `<temp>/voiceover-recordings`, profiles under `<data-dir>/profiles` (profiles.py), generations under `<data-dir>/generations`.
- Sidecar memory: `_generations`, `_generation_queue`, `_model_cache` (30 s TTL), `_vc_model` (server.py), plus Whisper and Qwen models in `tts.py`.

## Related

- [[building-blocks/frontend-state]] - Frontend state and Drive client
- [[building-blocks/sidecar-engine]] - Sidecar engine modules
- [[crosscutting/configuration]] - Configuration handling
