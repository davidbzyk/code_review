---
id: runtime/record-screen-flow
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Record screen flow"
description: "Recording runs from the Record button through MediaRecorder chunks to a file path or blob URL and the preview route."
domain: architecture
tags:
  - runtime
  - recording
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/+page.svelte
  - resource: src/lib/recorder.svelte.ts
  - resource: src-tauri/src/commands/recording.rs
relations:
  relates_to:
    - building-blocks/frontend-recorder
    - building-blocks/rust-recording-commands
    - runtime/process-recording-tauri
---
# Record screen flow

The flow starts in the main page and ends with a navigation to `/preview`.

## Steps

1. `handleRecord()` sets `recordingState` to `selecting` and calls `startRecording(captureMode, deviceId, webcam_enabled)` (src/routes/+page.svelte).
2. `startRecording` creates a session id with `generateSessionId()`, requests `getDisplayMedia` and `getUserMedia`, and builds a `MediaRecorder` (src/lib/recorder.svelte.ts).
3. `mediaRecorder.start(1000)` emits a chunk each second; `ondataavailable` handles each one.
4. In Tauri, each chunk is sent with `invoke('save_recording_chunk', { sessionId, chunk, chunkIndex })`, handled by `save_recording_chunk` (src-tauri/src/commands/recording.rs). In a browser it is pushed to `recordedChunks`.
5. The page sets `recordingState` to `recording` and starts a one-second interval that updates `recordingDuration`, minus paused time (src/routes/+page.svelte).
6. `handlePause()` calls `pauseRecording()` or `resumeRecording()` and records paused time.
7. `handleStop()` calls `stopRecording()`. In Tauri it invokes `finalize_recording`, which joins chunks into `<session_id>.webm`. In a browser it builds Blobs, stores them on `window`, and returns an object URL.
8. The page stores the result in `appState.recordingPath`, sets state `recorded`, and calls `goto('/preview')`.
9. `handleCancel()` calls `cancelRecording()` and `appState.reset()`.

## Related

[[building-blocks/frontend-recorder]], [[building-blocks/rust-recording-commands]], [[runtime/process-recording-tauri]]
