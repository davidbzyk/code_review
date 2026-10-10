---
id: building-blocks/frontend-recorder
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Frontend recorder and overlays
description: Browser media capture logic plus the region selector and webcam bubble components.
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
  - building-blocks/tauri-recording
  - building-blocks/frontend-state
---

# Frontend recorder and overlays

`recorder.svelte.ts` captures screen, microphone and optional webcam into a `MediaRecorder`, and two Svelte components draw the overlays.

## recorder.svelte.ts exports

- `startRecording(captureMode, audioDeviceId?, webcamEnabled?)`, `pauseRecording`, `resumeRecording`, `stopRecording`, `cancelRecording`.
- `generateSessionId`, `selectVideoMimeType`, `captureModeToDisplaySurface`, `getAudioDevices`.
- `computeWebcamBubbleRect(canvasW, canvasH, position)`: bubble diameter is 12% of width clamped to 100-240.
- `mapSelectionToSource`, `confirmRegionSelection`, `cancelRegionSelection` for region capture.
- Types `CaptureMode` (`fullscreen`, `window`, `region`) and `RegionRect`.
- In Tauri mode each 5-second chunk goes to `save_recording_chunk`; in browser mode chunks stay in memory and `blobStore` receives the blobs.
- A canvas compositor draws the screen (cropped to the region) and webcam bubble at 30 fps and feeds `captureStream(30)`.

## Components

- `RegionSelector.svelte` props `screenshotUrl`, `onSelect`, `onCancel`; a drag selection must be at least `MIN_SELECTION` (50) CSS pixels; Escape cancels.
- `WebcamBubble.svelte` shows a 120 px canvas preview at 15 fps while state is `recording` or `paused`, and `togglePosition` flips `webcam_position` and saves config.

## Uses

- Writes `appState` and calls `tauriInvoke` ([[building-blocks/frontend-state]], [[building-blocks/tauri-recording]]). Flow: [[runtime/record-screen]].

## Related

- [[runtime/record-screen]] - Record a screen session
- [[building-blocks/tauri-recording]] - Rust recording commands
- [[building-blocks/frontend-state]] - Frontend state and Drive client
