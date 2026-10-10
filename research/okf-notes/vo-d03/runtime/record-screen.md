---
id: runtime/record-screen
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Flow: record the screen"
description: "Steps from the Record button to a finished recording file or blob."
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
    - building-blocks/page-record
    - building-blocks/frontend-recorder
    - building-blocks/backend-recording
---

# Flow: record the screen

This flow takes a click on Record to a path or object URL stored in `appState.recordingPath`.

## Steps

1. `handleRecord()` in `src/routes/+page.svelte` sets `appState.recordingState = 'selecting'`.
2. It calls `startRecording()` in `src/lib/recorder.svelte.ts`, which makes a session id, requests `getDisplayMedia`, then `getUserMedia` for audio.
3. `startRecording()` builds a combined `MediaStream` and a `MediaRecorder`, and calls `mediaRecorder.start(1000)`.
4. Every slice triggers `ondataavailable`. In Tauri it invokes `save_recording_chunk`, which writes `chunk_NNNN.webm` in `commands/recording.rs`. In a browser it pushes the blob to `recordedChunks`; a second recorder fills `audioChunks`.
5. The page sets state `recording` and starts the duration timer.
6. `handlePause()` toggles `pauseRecording()` and `resumeRecording()`.
7. `handleStop()` calls `stopRecording()`. In Tauri the `onstop` handler invokes `finalize_recording`, which concatenates the chunks into `<session>.webm`. In a browser it creates blobs, stores `window.__voiceover_blob` and `window.__voiceover_audio_blob`, and returns an object URL.
8. The page stores the result in `appState.recordingPath`, sets `recorded`, and calls `goto('/preview')`.

`handleCancel()` calls `cancelRecording()` and `appState.reset()` instead of step 7.

## Related

- [building-blocks/page-record](../building-blocks/page-record.md)
- [building-blocks/frontend-recorder](../building-blocks/frontend-recorder.md)
- [building-blocks/backend-recording](../building-blocks/backend-recording.md)
- [runtime/process-recording-desktop](./process-recording-desktop.md)
