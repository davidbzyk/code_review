---
id: runtime/record-screen
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Record the screen"
description: "Steps from pressing Record to a finished recording file or in-memory blob."
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
  - resource: src/lib/RegionSelector.svelte
related:
  - building-blocks/frontend-recorder
  - building-blocks/rust-recording-files
  - runtime/process-recording
---
# Record the screen

Recording runs in the webview with MediaRecorder; Tauri mode saves 5-second chunks through Rust.

## Steps

1. `handleRecord` (src/routes/+page.svelte) sets state `selecting` and calls `startRecording`.
2. `startRecording` (src/lib/recorder.svelte.ts) makes a session id with `generateSessionId` and calls `getDisplayMedia` with a `displaySurface` hint.
3. In Tauri, for modes other than `window`, it minimizes the window, then restores it after the stream arrives.
4. In `region` mode it grabs one frame, sets state `selecting-region`, and waits for `confirmRegionSelection` or `cancelRegionSelection` from `RegionSelector`.
5. It requests microphone audio with `getUserMedia`, and the webcam when enabled.
6. When a region or webcam is active, a canvas compositor draws frames at 30 fps (`startCompositorLoop`) and `captureStream(30)` supplies the video track.
7. A `MediaRecorder` starts with `start(5000)`; each chunk goes to `save_recording_chunk` in Tauri, or into `recordedChunks` in the browser.
8. `handleStop` calls `stopRecording`. In Tauri it invokes `finalize_recording` (src-tauri/src/commands/recording.rs) and resolves with the file path. In the browser it builds blobs, stores them with `blobStore.setVideo` and `setAudio`, and resolves with an object URL.
9. The page stores `recordingPath`, sets state `recorded` and calls `goto('/preview')`.

In the browser an extra audio-only `MediaRecorder` also runs.

## Related

- [[building-blocks/frontend-recorder]]
- [[building-blocks/rust-recording-files]]
- [[runtime/process-recording]]
