---
id: building-blocks/home-screen
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Home Screen"
description: "The root route that picks capture options and starts, pauses and stops a recording."
domain: architecture
tags:
  - building-block
  - svelte
  - route
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/+page.svelte
---
# Home Screen

`src/routes/+page.svelte` is the main window view.

## Facts
- Capture modes: Full Screen, Window, Region (`captureModes`).
- `onMount` fills `audioDevices` through `getAudioDevices`.
- `handleRecord` sets state `selecting`, calls `startRecording`, sets `recording`, invokes `create_widget_window` in Tauri and starts a one-second timer for `recordingDuration`.
- `handleStop` calls `stopRecording`, stores `recordingPath`, sets `recorded`, then `goto('/preview')`.
- `handleCancel` calls `cancelRecording` and `appState.reset()`; `handlePause` toggles `paused`.
- Toggles for webcam and voice replacement write into `appState.config.preferences`; the voice select rewrites `is_default` on `appState.config.voices`.
- A button navigates to `/settings`.

## Related
- [[building-blocks/frontend-recorder]]
- [[building-blocks/preview-screen]]
- [[building-blocks/settings-screen]]
- [[runtime/record-screen-and-voice]]
