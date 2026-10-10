---
id: crosscutting/state-management
schema: okf/schemas/v1/architecture.json
type: Architecture
title: State Management
description: Where UI, session, process and file state are kept.
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
related:
  - building-blocks/frontend-state-and-config
  - building-blocks/rust-sidecar-manager
  - building-blocks/frontend-recorder
---

# State Management

State sits in four places.

## Facts

- UI state: `appState` fields `recordingState`, `recordingPath`, `outputPath`, `processingProgress`, `processingStage`, `errorMessage`, `recordingDuration`, `ffmpegAvailable` (src/lib/state.svelte.ts).
- Recorder module state: `mediaRecorder`, `audioRecorder`, `screenStream`, `audioStream`, `chunkIndex`, `sessionId`, `recordedChunks`, `audioChunks`, region fields (src/lib/recorder.svelte.ts). `cleanup()` resets them.
- Blobs: `blobStore` holds video and audio blobs for browser mode (src/lib/blobStore.ts).
- Host process state: `SidecarState` (child, port, data_dir, starting, `Notify`) and `HttpClient` are Tauri managed state (src-tauri/src/sidecar.rs, src-tauri/src/local_tts.rs).
- Sidecar state: `_generations`, `_generation_queue`, `_vc_model`, `_model_cache` with a TTL in server.py; `_qwen_model` and `_whisper_model` in tts.py.
- Files: config in `config.json`, profiles under `profiles/`, generations under `generations/`, models under `models/`, prompt cache under `cache/` in the data dir.
- Completed generations older than one hour are removed by `_cleanup_generations`.

## Related

- [Frontend State and Config](../building-blocks/frontend-state-and-config.md)
- [Rust Sidecar Manager](../building-blocks/rust-sidecar-manager.md)
- [Frontend Recorder](../building-blocks/frontend-recorder.md)
