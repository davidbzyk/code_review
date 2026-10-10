---
id: building-blocks/frontend-recorder
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Frontend Recorder
description: Screen, microphone and webcam capture with MediaRecorder, plus region selection and the webcam bubble.
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
related:
  - runtime/record-screen
  - building-blocks/frontend-state-and-config
  - building-blocks/rust-recording-commands
  - building-blocks/frontend-routes
---

# Frontend Recorder

`recorder.svelte.ts` owns the capture session; two components support region mode and the webcam preview.

## recorder.svelte.ts exports

- `startRecording(captureMode, audioDeviceId?, webcamEnabled?)`, `pauseRecording`, `resumeRecording`, `stopRecording`, `cancelRecording`.
- `generateSessionId` returns `rec-<time>-<random>`; `selectVideoMimeType` prefers `video/webm;codecs=vp8,opus`.
- `captureModeToDisplaySurface` maps `window` to `window`, other modes to `monitor`.
- `getAudioDevices`, `computeWebcamBubbleRect`, `mapSelectionToSource`, `confirmRegionSelection`, `cancelRegionSelection`.
- Types `CaptureMode` (`fullscreen`, `window`, `region`) and `RegionRect`.

## Behaviour

- Video `MediaRecorder` uses `videoBitsPerSecond: 2_500_000` and `start(5000)`, so chunks arrive every 5 seconds.
- Under Tauri each chunk goes to `save_recording_chunk`; in a browser chunks stay in `recordedChunks`, and a separate audio-only recorder fills `audioChunks`.
- A canvas compositor draws the screen and webcam bubble into the recorded stream.

## Components

- `RegionSelector.svelte`: props `screenshotUrl`, `onSelect`, `onCancel`; minimum selection 50 CSS pixels.
- `WebcamBubble.svelte`: canvas preview at 15 fps from `appState.webcamVideoEl`; `togglePosition` flips `webcam_position`.

## Related

- [Flow: Record the Screen](../runtime/record-screen.md)
- [Frontend State and Config](./frontend-state-and-config.md)
- [Rust Recording Commands](./rust-recording-commands.md)
- [Frontend Routes](./frontend-routes.md)
