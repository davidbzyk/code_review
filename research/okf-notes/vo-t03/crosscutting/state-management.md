---
id: crosscutting/state-management
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "State management"
description: "Reactive app state, module state and server-side state."
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
  - building-blocks/frontend-state-and-utils
  - crosscutting/configuration
---
# State management

State lives in four places.

## Facts

- `appState` (Svelte 5 `$state` fields) is the shared UI and config state; `reset()` clears recording fields and stops webcam tracks (src/lib/state.svelte.ts).
- `RecordingState` values: `ready`, `selecting`, `selecting-region`, `recording`, `paused`, `recorded`, `processing`, `complete`, `saved`.
- `recorder.svelte.ts` holds module-level variables for the recorders, streams, compositor canvas and region callback; `cleanup()` resets them.
- `blobStore` holds the browser-mode video and audio blobs in module variables.
- The host keeps `SidecarState` (child, port, data dir, starting flag) as Tauri managed state (src-tauri/src/sidecar.rs).
- The sidecar keeps `_generations` and `_generation_queue` in memory and `_whisper_model`, `_qwen_model` in `tts.py`.
- Persistent state: `config.json`, the keychain entry, and the sidecar data folder.

## Related

- [[building-blocks/frontend-state-and-utils]]
- [[crosscutting/configuration]]
