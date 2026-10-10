---
id: building-blocks/frontend-state
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Frontend State and Bridges"
description: "The AppState store, the Tauri invoke wrapper, the blob store and the lib barrel file."
domain: architecture
tags:
  - building-blocks
  - frontend
  - state
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/lib/state.svelte.ts
  - resource: src/lib/tauri.ts
  - resource: src/lib/blobStore.ts
  - resource: src/lib/index.ts
relations:
  relates_to:
    - crosscutting/state
    - building-blocks/frontend-recorder
    - building-blocks/route-preview
    - runtime/config-load-save
---

These four files in `src/lib/` hold shared state and the bridge to the Rust side.

## Facts

- `AppState` (`src/lib/state.svelte.ts`) is a class with `$state` fields: `config`, `webcamStream`, `webcamVideoEl`, `recordingState`, `recordingPath`, `outputPath`, `processingProgress`, `processingStage`, `errorMessage`, `recordingDuration`, `ffmpegAvailable`. The module exports one instance, `appState`.
- Derived values: `selectedVoice` (default voice, else first voice, else null) and `isConfigured` (API key non-empty and at least one voice).
- Methods: `loadConfig()`, `saveConfig()`, `reset()`; see [Config load and save flow](../runtime/config-load-save.md).
- `isTauri()` is true when `window.__TAURI_INTERNALS__` is set.
- `RecordingState` values: `ready`, `selecting`, `recording`, `paused`, `recorded`, `processing`, `complete`, `saved`.
- `tauriInvoke<T>(cmd, args)` in `src/lib/tauri.ts` dynamically imports `@tauri-apps/api/core` and calls `invoke`.
- `blobStore` in `src/lib/blobStore.ts` keeps module-level `videoBlob` and `audioBlob` with `setVideo`, `getVideo`, `setAudio`, `getAudio`, `clear`.
- `src/lib/index.ts` holds one comment line and no exports.

## Related

- [State concern](../crosscutting/state.md)
- [Frontend recorder](frontend-recorder.md)
- [Preview route](route-preview.md)
