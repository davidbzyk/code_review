---
id: crosscutting/state-and-storage
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "State and Storage"
description: "Where runtime state and files are kept."
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
  - resource: src-tauri/src/commands/recording.rs
  - resource: src-tauri/src/pipeline.rs
related:
  - building-blocks/frontend-state
  - runtime/record-flow
---
# State and Storage

State lives in a Svelte rune class, module variables, temp files and the app data folder.

## Facts
- `AppState` uses `$state` and `$derived` fields; `recordingState` takes nine values: `ready`, `selecting`, `selecting-region`, `recording`, `paused`, `recorded`, `processing`, `complete`, `saved` (src/lib/state.svelte.ts).
- `blobStore` keeps the browser-mode video and audio Blobs in module variables (src/lib/blobStore.ts).
- Recorder streams, recorders and compositor handles are module-level `let` variables (src/lib/recorder.svelte.ts).
- Chunks are written to `<temp>/voiceover-recordings/<session>/chunk_NNNN.webm`, joined into `<session>.webm` (src-tauri/src/commands/recording.rs).
- Pipeline temp files `extracted-<ts>.wav` and `transformed-<ts>.(wav|mp3)` sit beside the recording and are removed after success (src-tauri/src/pipeline.rs).
- localStorage key `voiceover-config` holds sanitized config.

## Related
- [Frontend State](../building-blocks/frontend-state.md)
- [Record Flow](../runtime/record-flow.md)
