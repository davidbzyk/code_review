---
id: runtime/record-screen
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Record Screen Flow"
description: "From pressing Record to a finished recording path."
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

A recording is captured in the webview and saved as chunks.

## Steps

1. `handleRecord()` in `src/routes/+page.svelte` sets `recordingState = 'selecting'` and calls `startRecording`.
2. `startRecording` (`src/lib/recorder.svelte.ts`) creates a session id with `generateSessionId()`.
3. It calls `navigator.mediaDevices.getDisplayMedia` (screen), then `getUserMedia` (microphone).
4. With webcam enabled, `getWebcamStream()` and the canvas compositor (`startCompositorLoop`) supply the video track.
5. A `MediaRecorder` with `selectVideoMimeType()` starts with a 5000 ms timeslice.
6. Each `ondataavailable` chunk: in Tauri, `tauriInvoke('save_recording_chunk', { sessionId, chunk, chunkIndex })`; in the browser, pushed to `recordedChunks`. Browser mode also runs `audioRecorder` for an audio-only track.
7. `save_recording_chunk` (`src-tauri/src/commands/recording.rs`) validates the id and writes `chunk_NNNN.webm`.
8. `handleStop()` calls `stopRecording()`. In Tauri it invokes `finalize_recording` and resolves the joined `.webm` path; in the browser it builds blobs, calls `blobStore.setVideo` and `setAudio`, and resolves an object URL.
9. The page stores the path in `appState.recordingPath`, sets `recorded` and calls `goto('/preview')`.

## Related

- [Frontend recorder](../building-blocks/frontend-recorder.md)
- [Rust recording commands](../building-blocks/rust-recording-commands.md)
- [Process recording, desktop](process-recording-tauri.md)
