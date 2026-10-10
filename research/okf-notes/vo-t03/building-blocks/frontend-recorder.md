---
id: building-blocks/frontend-recorder
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Frontend recorder"
description: "Screen, microphone and webcam capture, plus the region selector and the webcam bubble."
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
  - building-blocks/rust-recording-files
  - building-blocks/frontend-state-and-utils
---
# Frontend recorder

The recorder module drives the browser media APIs and hands the finished recording to Rust or to memory.

## Public functions of recorder.svelte.ts

- `startRecording(captureMode, audioDeviceId?, webcamEnabled?)`, `pauseRecording`, `resumeRecording`, `stopRecording`, `cancelRecording`.
- `getAudioDevices`, `selectVideoMimeType`, `generateSessionId`, `captureModeToDisplaySurface`.
- `computeWebcamBubbleRect`, `mapSelectionToSource`, `confirmRegionSelection`, `cancelRegionSelection`.
- Types `CaptureMode` (`fullscreen`, `window`, `region`) and `RegionRect`.

## Components

- `RegionSelector.svelte`: draws a drag rectangle over a screenshot; minimum selection `MIN_SELECTION = 50`; Escape calls `onCancel`; confirm calls `onSelect` with `mapSelectionToSource` output.
- `WebcamBubble.svelte`: a 120 px canvas preview at 15 fps that draws from `appState.webcamVideoEl`; `togglePosition` flips `webcam_position` and calls `saveConfig`.

## Calls

- Tauri commands `save_recording_chunk` and `finalize_recording` through `tauriInvoke`.
- `appState`, `logger`, `blobStore`.
- `@tauri-apps/api/window` to minimize and restore the window around the screen picker.

Code between `v8 ignore` markers needs a browser runtime and is excluded from coverage.

## Related

- [[runtime/record-screen]]
- [[building-blocks/rust-recording-files]]
- [[building-blocks/frontend-state-and-utils]]
