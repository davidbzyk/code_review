---
id: runtime/record-screen-flow
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Record screen flow"
description: "From the record button to the /preview route."
domain: architecture
tags:
  - runtime
  - recording
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
architecture_layer: runtime
sources:
  - resource: src/routes/+page.svelte
  - resource: src/lib/recorder.svelte.ts
  - resource: src-tauri/src/commands/recording.rs
related:
  - building-blocks/route-home
  - building-blocks/frontend-recorder
  - building-blocks/backend-recording-commands
  - runtime/process-recording-desktop-flow
---

# Record screen flow

A recording runs as 1-second chunks and ends on `/preview`.

## Steps
1. `handleRecord()` sets `recordingState` to `selecting` and calls `startRecording` (src/routes/+page.svelte).
2. `startRecording` creates a session id `rec-<time>-<random>`, calls `getDisplayMedia`, then `getUserMedia` (src/lib/recorder.svelte.ts).
3. It builds a `MediaRecorder` on the combined stream and calls `start(1000)` (src/lib/recorder.svelte.ts).
4. Tauri mode: `ondataavailable` invokes `save_recording_chunk`, which writes `chunk_NNNN.webm` (src/lib/recorder.svelte.ts, src-tauri/src/commands/recording.rs).
5. Browser mode: chunks are pushed to `recordedChunks`; an audio-only recorder fills `audioChunks` (src/lib/recorder.svelte.ts).
6. `handleRecord()` sets state `recording` and starts the duration timer (src/routes/+page.svelte).
7. `handleStop()` calls `stopRecording()`; on `onstop`, Tauri invokes `finalize_recording`, browser builds blobs and a blob URL (src/lib/recorder.svelte.ts).
8. The path goes to `appState.recordingPath`, state becomes `recorded`, `goto('/preview')` runs (src/routes/+page.svelte).

## Related

- [[building-blocks/route-home]]
- [[building-blocks/frontend-recorder]]
- [[building-blocks/backend-recording-commands]]
- [[runtime/process-recording-desktop-flow]]
