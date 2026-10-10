---
id: building-blocks/widget-screen
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Widget Screen"
description: "The /widget route shown in the floating recording window."
domain: architecture
tags:
  - building-block
  - svelte
  - route
  - widget
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/widget/+page.svelte
  - resource: src/routes/widget/+layout.ts
---
# Widget Screen

`src/routes/widget/+page.svelte` shows a timer with pause, stop and cancel controls.

## Facts
- `duration` increments every second while `isPaused` is false.
- It listens to the event `widget-voice-name` and stores the payload in `voiceName`.
- `handlePause` toggles `isPaused` and invokes `plugin:event|emit` with `recording-pause` or `recording-resume`.
- `handleStop` emits `recording-stop`, then invokes `close_widget_window`; `handleCancel` emits `recording-cancel` then closes.
- `formatTime` renders mm:ss.

## Related
- [[runtime/widget-controls]]
- [[building-blocks/window-commands]]
- [[interfaces/widget-events]]
