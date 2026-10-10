---
id: building-blocks/frontend-recorder
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Frontend Recorder
description: Screen, microphone and webcam capture in the webview.
domain: architecture
tags:
  - building-block
  - frontend
  - recording
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/lib/recorder.svelte.ts
  - resource: src/lib/RegionSelector.svelte
  - resource: src/lib/WebcamBubble.svelte
relations:
  relates_to:
    - runtime/record-and-process-recording
    - building-blocks/rust-recording-and-library
    - building-blocks/frontend-state-and-ipc
---
# Frontend Recorder

The recorder module turns a browser media stream into recorded video data and hands it to Rust.

## Functions in `recorder.svelte.ts`

- `startRecording(captureMode, audioDeviceId, webcamEnabled)` calls `getDisplayMedia`, minimizes the Tauri window while the picker shows, builds a combined `MediaStream`, and starts a `MediaRecorder` with `start(5000)` and `videoBitsPerSecond: 2_500_000`.
- `selectVideoMimeType`, `captureModeToDisplaySurface`, `generateSessionId`, `getAudioDevices`.
- `pauseRecording`, `resumeRecording`, `stopRecording`, `cancelRecording`.
- `computeWebcamBubbleRect` places the webcam bubble on the canvas.
- `mapSelectionToSource`, `confirmRegionSelection`, `cancelRegionSelection` serve region capture.

## Storage paths

- In Tauri, each chunk goes to `save_recording_chunk`; `stopRecording` calls `finalize_recording`.
- In a browser, chunks stay in memory, and `stopRecording` stores blobs with `blobStore.setVideo` and `setAudio`.

## Components

- `RegionSelector.svelte` lets the user draw a rectangle and calls `mapSelectionToSource`.
- `WebcamBubble.svelte` draws a preview loop and has `togglePosition` between bottom-left and bottom-right.

## Uses

`src/lib/state.svelte.ts`, `src/lib/blobStore.ts`, `src/lib/tauri.ts`.

## Related

- [Flow: Record and Process a Recording](../runtime/record-and-process-recording.md)
- [Rust Recording and Library](rust-recording-and-library.md)
- [Frontend State and IPC](frontend-state-and-ipc.md)
