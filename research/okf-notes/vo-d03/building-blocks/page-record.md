---
id: building-blocks/page-record
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Record page"
description: "Route / that selects a microphone and capture mode, then starts, pauses and stops a recording."
domain: architecture
tags:
  - building-block
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
---

# Record page

`src/routes/+page.svelte` is the home route; it drives `src/lib/recorder.svelte.ts` and moves to `/preview` when recording stops.

## Functions

- `onMount`: calls `getAudioDevices()` and selects the first device id.
- `handleRecord()`: sets `appState.recordingState` to `selecting`, calls `startRecording(captureMode, selectedDeviceId, appState.config.preferences.webcam_enabled)`, sets `recording`, and starts a one-second `setInterval` that updates `appState.recordingDuration`. On error it resets to `ready` and sets `appState.errorMessage`.
- `handleStop()`: `stopRecording()`, stores the result in `appState.recordingPath`, sets `recorded`, `goto('/preview')`.
- `handleCancel()`: `cancelRecording()` then `appState.reset()`.
- `handlePause()`: toggles between `pauseRecording()` and `resumeRecording()` and the `paused` and `recording` states.
- `formatTime(seconds)`: `mm:ss`.
- `captureModes`: `fullscreen`, `window`, `region` with labels and icons.
- A top-bar button calls `goto('/settings')`; toggle buttons flip `preferences.webcam_enabled` and `preferences.voice_replacement_enabled`.

## Uses

`appState`, `isTauri` from [frontend-state](./frontend-state.md); recorder functions from [frontend-recorder](./frontend-recorder.md).

## Related

- [runtime/record-screen](../runtime/record-screen.md)
- [building-blocks/page-preview](./page-preview.md)
- [building-blocks/page-settings](./page-settings.md)
