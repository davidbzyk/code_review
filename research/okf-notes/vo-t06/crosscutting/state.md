---
id: crosscutting/state
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Application State"
description: "Where mutable state lives in the webview and on the Rust side."
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
  - resource: src-tauri/src/commands/recording.rs
relations:
  relates_to:
    - building-blocks/frontend-state
    - building-blocks/frontend-recorder
---

Page state is held in one `AppState` instance; recording bytes live in module variables or temp files.

## Facts

- `appState` holds `recordingState`, paths, progress and `config` as Svelte `$state` (`src/lib/state.svelte.ts`).
- `reset()` stops webcam tracks and returns the fields to their initial values.
- `blobStore` keeps the browser-mode video and audio blobs in module variables (`src/lib/blobStore.ts`).
- `recorder.svelte.ts` keeps `mediaRecorder`, `screenStream`, `audioStream`, `chunkIndex`, `sessionId` and canvas objects as module variables.
- Desktop recordings sit in `<temp>/voiceover-recordings` until `finalize_recording` or `cleanup_temp` removes them.
- The Rust side holds no global state apart from the keychain entry and `config.json`.

## Related

- [Frontend state](../building-blocks/frontend-state.md)
- [Frontend recorder](../building-blocks/frontend-recorder.md)
