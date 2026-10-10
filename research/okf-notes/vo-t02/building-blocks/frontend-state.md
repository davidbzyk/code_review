---
id: building-blocks/frontend-state
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Frontend State"
description: "Shared reactive app state, the Tauri bridge, the in-memory blob store and the logger."
domain: architecture
tags:
  - building-block
  - frontend
  - state
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/lib/state.svelte.ts
  - resource: src/lib/tauri.ts
  - resource: src/lib/blobStore.ts
  - resource: src/lib/logger.ts
  - resource: src/lib/index.ts
related:
  - crosscutting/state-and-storage
  - crosscutting/logging
  - runtime/config-load-and-save
---
# Frontend State

This block holds the singleton `appState`, the `tauriInvoke` wrapper, `blobStore` and `logger`.

## Files
- src/lib/state.svelte.ts: class `AppState` with `config`, `recordingState`, `recordingPath`, `outputPath`, `processingProgress`, `processingStage`, `errorMessage`, `ffmpegAvailable`; derived `selectedVoice` and `isConfigured`; methods `loadConfig`, `saveConfig`, `reset`. Exports `appState`, `isTauri`, and the types `Voice`, `GoogleDrive`, `AppConfig`, `RecordingState`.
- src/lib/tauri.ts: `tauriInvoke` imports `@tauri-apps/api/core` on demand and calls `invoke`.
- src/lib/blobStore.ts: module-private `videoBlob` and `audioBlob` behind `setVideo`, `getVideo`, `setAudio`, `getAudio`, `clear`.
- src/lib/logger.ts: the `logger` object.
- src/lib/index.ts: a single comment line.

## Used by
Every route and `recorder.svelte.ts`.

## Related
- [State and Storage](../crosscutting/state-and-storage.md)
- [Logging](../crosscutting/logging.md)
- [Config Load and Save](../runtime/config-load-and-save.md)
