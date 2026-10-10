---
id: building-blocks/page-widget
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Widget page"
description: "Route /widget, the small always-on-top recording control window."
domain: architecture
tags:
  - building-block
  - frontend
  - route
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/widget/+page.svelte
  - resource: src/routes/widget/+layout.ts
relations:
  relates_to:
    - building-blocks/backend-window
    - interfaces/app-events
---

# Widget page

`src/routes/widget/+page.svelte` renders the 340x80 floating window and sends control events to the main window.

## Behaviour

- `onMount`: when `isTauri()`, starts a one-second counter that increments `duration` unless `isPaused`; listens for the Tauri event `widget-voice-name` and stores the payload in `voiceName`. The cleanup clears the timer and unlistens.
- `handlePause()`: flips `isPaused` and invokes `plugin:event|emit` with `recording-pause` or `recording-resume`.
- `handleStop()`: clears the timer, `emit('recording-stop')`, invokes `close_widget_window`.
- `handleCancel()`: clears the timer, `emit('recording-cancel')`, invokes `close_widget_window`.
- `formatTime(seconds)`: `mm:ss`.

All handlers return early when `isTauri()` is false.

## Window

The window is created by the Rust command `create_widget_window` (`src-tauri/src/commands/window.rs`) with URL `/widget`. No file under `src/` invokes `create_widget_window`, and no file under `src/` listens for `recording-stop`, `recording-cancel`, `recording-pause` or `recording-resume`.

## Related

- [building-blocks/backend-window](./backend-window.md)
- [interfaces/app-events](../interfaces/app-events.md)
- [building-blocks/page-record](./page-record.md)
