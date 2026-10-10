---
id: runtime/record-flow
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Record Flow"
description: "From the Record button to a finalized WebM file and the preview page."
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
  - resource: src/lib/blobStore.ts
related:
  - building-blocks/frontend-recording
  - interfaces/tauri-commands-recording-and-pipeline
  - runtime/process-recording-desktop
---
# Record Flow

A recording runs in the webview and stores its chunks through Rust under Tauri, or in memory in a browser.

## Steps
1. `handleRecord` (src/routes/+page.svelte) sets state `selecting` and calls `startRecording`.
2. `startRecording` (src/lib/recorder.svelte.ts) calls `generateSessionId`, then `navigator.mediaDevices.getDisplayMedia`. Under Tauri, for modes other than `window`, it minimizes the window and restores it after selection.
3. In `region` mode it grabs a frame into `appState.regionScreenshot`; `RegionSelector` calls `confirmRegionSelection` or `cancelRegionSelection`.
4. It requests microphone audio with `getUserMedia` and, if enabled, the webcam with `getWebcamStream`.
5. With a webcam or region it draws to a canvas in `startCompositorLoop` (30 fps) and records `captureStream(30)`.
6. A `MediaRecorder` starts with `start(5000)`. Each chunk goes to `save_recording_chunk` (src-tauri/src/commands/recording.rs) under Tauri, or into `recordedChunks` in a browser. A second audio-only recorder runs in browser mode.
7. `handleStop` calls `stopRecording`. Under Tauri it invokes `finalize_recording`, which concatenates `chunk_NNNN.webm` files in sorted order into `<session>.webm` and removes the chunk folder. In a browser it builds Blobs and calls `blobStore.setVideo` and `blobStore.setAudio`.
8. `handleStop` stores `appState.recordingPath`, sets state `recorded`, and calls `goto('/preview')`.

## Related
- [Frontend Recording](../building-blocks/frontend-recording.md)
- [Tauri Commands: Recording and Pipeline](../interfaces/tauri-commands-recording-and-pipeline.md)
- [Process Recording on Desktop](./process-recording-desktop.md)
