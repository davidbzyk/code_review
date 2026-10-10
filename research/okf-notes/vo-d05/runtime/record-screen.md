---
id: runtime/record-screen
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Record a screen session
description: Flow from pressing Record to a finalized recording file and the navigation to the preview page.
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
related:
  - building-blocks/frontend-recorder
  - building-blocks/tauri-recording
  - runtime/process-recording-elevenlabs
---

# Record a screen session

This flow turns the Record button into one `.webm` file (Tauri mode) or in-memory blobs (browser mode).

## Steps

1. `handleRecord` (src/routes/+page.svelte) sets state `selecting` and calls `startRecording`.
2. `startRecording` (src/lib/recorder.svelte.ts) makes a session id with `generateSessionId` and calls `getDisplayMedia`; in Tauri, for non-window capture, it minimizes the window while the picker shows and restores it afterwards.
3. For `region` mode it captures one frame, sets state `selecting-region`, and waits for `confirmRegionSelection` or `cancelRegionSelection`.
4. It requests the microphone with `getUserMedia`, and the webcam through `getWebcamStream` when enabled.
5. If a region or webcam is used, a canvas compositor feeds `captureStream(30)`; otherwise the screen tracks are used directly.
6. A `MediaRecorder` starts with 5000 ms timeslices and 2.5 Mbit/s video; `selectVideoMimeType` prefers `video/webm;codecs=vp8,opus`.
7. Each chunk goes to `save_recording_chunk` (Tauri), which writes `chunk_NNNN.webm` (src-tauri/src/commands/recording.rs); in browser mode chunks are pushed to `recordedChunks`, and a separate audio-only recorder also runs.
8. `handlePause` calls `pauseRecording` / `resumeRecording` and tracks paused time for the timer.
9. `handleStop` calls `stopRecording`; in Tauri it invokes `finalize_recording`, which concatenates the chunks into `<session>.webm`; in browser mode it creates a blob URL and stores blobs in `blobStore`.
10. `appState.recordingPath` is set, state becomes `recorded`, and `goto('/preview')` runs.

If the screen track ends externally, the listener calls `cancelRecording`.

## Related

- [[building-blocks/frontend-recorder]] - Frontend recorder and overlays
- [[building-blocks/tauri-recording]] - Rust recording commands
- [[runtime/process-recording-elevenlabs]] - Process recording with ElevenLabs
