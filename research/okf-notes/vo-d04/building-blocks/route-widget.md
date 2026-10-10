---
id: building-blocks/route-widget
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Route /widget"
description: "Small always-on-top recording widget page."
domain: architecture
tags:
  - frontend
  - route
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
architecture_layer: building-blocks
sources:
  - resource: src/routes/widget/+page.svelte
related:
  - runtime/widget-window-flow
  - building-blocks/backend-window-commands
  - interfaces/window-events
---

# Route /widget

`src/routes/widget/+page.svelte` shows a timer with pause, stop and cancel buttons.

## Facts (src/routes/widget/+page.svelte)
- Runs only when `isTauri()`; a one-second interval raises `duration` unless `isPaused`.
- Listens to the event `widget-voice-name` and shows the payload as `voiceName`.
- `handlePause()` emits `recording-pause` or `recording-resume` through `invoke('plugin:event|emit')`.
- `handleStop()` emits `recording-stop`, then invokes `close_widget_window`.
- `handleCancel()` emits `recording-cancel`, then invokes `close_widget_window`.
- The effect cleanup clears the interval and unlistens.

## Related

- [[runtime/widget-window-flow]]
- [[building-blocks/backend-window-commands]]
- [[interfaces/window-events]]
