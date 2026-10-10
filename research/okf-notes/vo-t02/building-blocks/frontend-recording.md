---
id: building-blocks/frontend-recording
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Frontend Recording"
description: "Browser media capture, canvas compositing and region selection."
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
  - runtime/record-flow
  - building-blocks/frontend-state
  - interfaces/tauri-commands-recording-and-pipeline
---
# Frontend Recording

The recording block turns screen, microphone and optional webcam streams into a WebM file.

## Public functions (src/lib/recorder.svelte.ts)
`startRecording`, `stopRecording`, `pauseRecording`, `resumeRecording`, `cancelRecording`, `getAudioDevices`, `generateSessionId`, `selectVideoMimeType`, `captureModeToDisplaySurface`, `mapSelectionToSource`, `computeWebcamBubbleRect`, `confirmRegionSelection`, `cancelRegionSelection`. Types `CaptureMode` and `RegionRect`.

## Components
- src/lib/RegionSelector.svelte: draws a selection over `regionScreenshot`; minimum selection `MIN_SELECTION = 50`; calls `mapSelectionToSource`.
- src/lib/WebcamBubble.svelte: canvas preview at 15 fps (`PREVIEW_FPS`) from `appState.webcamVideoEl`; `togglePosition` flips `webcam_position` and saves config.

## Uses
- `appState`, `isTauri` from src/lib/state.svelte.ts; `blobStore`; `logger`; `tauriInvoke`.
- Tauri commands `save_recording_chunk` and `finalize_recording`.

## Related
- [Record Flow](../runtime/record-flow.md)
- [Frontend State](./frontend-state.md)
- [Tauri Commands: Recording and Pipeline](../interfaces/tauri-commands-recording-and-pipeline.md)
