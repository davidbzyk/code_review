---
id: crosscutting/state-management
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "State management"
description: "A single AppState class holds recording, processing and config state in Svelte runes, and module variables hold the live recorders."
domain: architecture
tags:
  - crosscutting
  - state
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/lib/state.svelte.ts
  - resource: src/lib/recorder.svelte.ts
  - resource: src/routes/+page.svelte
  - resource: src/routes/preview/+page.svelte
relations:
  relates_to:
    - building-blocks/frontend-state
    - building-blocks/frontend-recorder
    - runtime/record-screen-flow
---
# State management

State is split between the reactive singleton and non-reactive module variables.

## Facts

- `appState` is a class instance with `$state` fields and two `$derived` values (src/lib/state.svelte.ts).
- Pages read and write `appState.recordingState` through the values `ready`, `selecting`, `recording`, `paused`, `recorded`, `saved` (src/routes/+page.svelte, src/routes/preview/+page.svelte).
- `reset()` returns the recording fields to their initial values but leaves `config` alone.
- src/lib/recorder.svelte.ts keeps `mediaRecorder`, `audioRecorder`, `screenStream`, `audioStream`, `chunkIndex`, `sessionId`, `recordedChunks` and `audioChunks` as module-level variables.
- In browser mode the recorded blobs are passed between routes on `window.__voiceover_blob` and `window.__voiceover_audio_blob`.
- Rust keeps no shared state; per-session chunk folders live under the temp directory (src-tauri/src/commands/recording.rs).

## Related

[[building-blocks/frontend-state]], [[building-blocks/frontend-recorder]], [[runtime/record-screen-flow]]
