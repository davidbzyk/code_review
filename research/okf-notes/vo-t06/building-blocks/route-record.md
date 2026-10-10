---
id: building-blocks/route-record
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Record Route"
description: "The home page at / where capture mode is chosen and recording is started, paused or stopped."
domain: architecture
tags:
  - building-blocks
  - frontend
  - route
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/+page.svelte
relations:
  relates_to:
    - runtime/record-screen
    - building-blocks/frontend-recorder
    - building-blocks/route-preview
---

`src/routes/+page.svelte` is the first screen: it controls the recorder and moves on to the preview route.

## Facts

- Local state: `captureMode` (default `fullscreen`), `audioDevices`, `selectedDeviceId`, `isStarting`, pause counters and a timer handle.
- `captureModes` lists `fullscreen` ("Full Screen"), `window` and `region`.
- On mount it calls `getAudioDevices()` and selects the first device.
- `handleRecord()` sets `recordingState` to `selecting`, calls `startRecording(captureMode, selectedDeviceId, webcam_enabled)`, then sets `recording` and starts a one-second timer that writes `appState.recordingDuration` minus paused time.
- `handlePause()` toggles between `pauseRecording()` and `resumeRecording()` and the `paused` and `recording` states.
- `handleStop()` calls `stopRecording()`, stores the result in `appState.recordingPath`, sets `recorded` and calls `goto('/preview')`.
- `handleCancel()` calls `cancelRecording()` and `appState.reset()`.
- A top bar button calls `goto('/settings')`; the page renders `WebcamBubble` and shows `appState.errorMessage` with a dismiss button.

## Related

- [Record screen flow](../runtime/record-screen.md)
- [Frontend recorder](frontend-recorder.md)
- [Preview route](route-preview.md)
