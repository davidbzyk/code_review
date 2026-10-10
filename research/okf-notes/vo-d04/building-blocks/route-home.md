---
id: building-blocks/route-home
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Route / (record page)"
description: "The home page: capture options, voice choice and record controls."
domain: architecture
tags:
  - frontend
  - route
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
architecture_layer: building-blocks
sources:
  - resource: src/routes/+page.svelte
related:
  - building-blocks/frontend-recorder
  - building-blocks/frontend-state
  - runtime/record-screen-flow
  - building-blocks/route-preview
---

# Route / (record page)

`src/routes/+page.svelte` lets the user pick options and run a recording.

## Facts (src/routes/+page.svelte)
- `onMount` loads microphones with `getAudioDevices()` and selects the first.
- `handleRecord()` sets `appState.recordingState` to `selecting`, calls `startRecording`, sets `recording` and starts a one-second timer that updates `appState.recordingDuration`.
- `handlePause()` toggles `pauseRecording` and `resumeRecording`.
- `handleStop()` calls `stopRecording()`, stores `appState.recordingPath`, sets state `recorded` and runs `goto('/preview')`.
- `handleCancel()` calls `cancelRecording()` and `appState.reset()`.
- Options: capture mode buttons, microphone select, webcam toggle, voice select (calls `appState.saveConfig()` on change), voice replacement toggle.
- The record button is disabled while starting or when `appState.ffmpegAvailable` is false.
- A Settings button runs `goto('/settings')`; errors show in `appState.errorMessage`.

## Related

- [[building-blocks/frontend-recorder]]
- [[building-blocks/frontend-state]]
- [[runtime/record-screen-flow]]
- [[building-blocks/route-preview]]
