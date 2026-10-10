---
id: building-blocks/frontend-record-page
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Record page and widget page
description: The home route that starts a recording and the floating widget route shown during capture.
domain: architecture
tags:
  - building-block
  - frontend
  - ui
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/+page.svelte
  - resource: src/routes/widget/+page.svelte
related:
  - building-blocks/frontend-recorder
  - building-blocks/backend-window-commands
  - runtime/record-a-session
  - interfaces/tauri-events
---

src/routes/+page.svelte is the record screen at `/`; src/routes/widget/+page.svelte is the small always-on-top control window at `/widget`.

## +page.svelte
- State: `captureMode`, `audioDevices`, `selectedDeviceId`, `isStarting`.
- `onMount` lists audio inputs with `getAudioDevices()`.
- `handleRecord()`: sets `recordingState` to `selecting`, calls `startRecording`, sets `recording`; under Tauri invokes `create_widget_window` and registers `listen` handlers for `recording-stop` and `recording-cancel`; starts a one-second duration timer.
- `handleStop()`: `stopRecording()`, stores `recordingPath`, state `recorded`, `goto('/preview')`.
- `handleCancel()`, `handlePause()`, `formatTime()`.
- Capture mode options: Full Screen, Window, Region. A button goes to `/settings`.

## widget/+page.svelte
- Own `duration`, `isPaused`, `voiceName`; a one-second timer in `onMount`.
- Listens to the event `widget-voice-name`.
- `handlePause()` emits `recording-pause` or `recording-resume` through `invoke('plugin:event|emit', ...)`.
- `handleStop()` emits `recording-stop`, then invokes `close_widget_window`; `handleCancel()` does the same with `recording-cancel`.

## Uses
[[building-blocks/frontend-recorder]], `appState`, [[building-blocks/backend-window-commands]].

## Related
[[runtime/record-a-session]], [[interfaces/tauri-events]]
