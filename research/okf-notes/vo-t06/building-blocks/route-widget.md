---
id: building-blocks/route-widget
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Widget Route"
description: "The page at /widget shown in the small recording window."
domain: architecture
tags:
  - building-blocks
  - frontend
  - route
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/widget/+page.svelte
relations:
  relates_to:
    - interfaces/tauri-events
    - building-blocks/route-shell
    - building-blocks/rust-window-commands
---

`src/routes/widget/+page.svelte` shows a timer with pause, stop and cancel buttons inside the widget window.

## Facts

- When `isTauri()` is true, a one-second interval increments `duration` unless `isPaused`.
- It listens for the Tauri event `widget-voice-name` and shows the payload next to the status text.
- `handlePause()` flips `isPaused` and invokes `plugin:event|emit` with `recording-pause` or `recording-resume`.
- `handleStop()` emits `recording-stop`, then invokes `close_widget_window`.
- `handleCancel()` emits `recording-cancel`, then invokes `close_widget_window`.
- No other file in `src/` or `src-tauri/src/` listens for these four events or emits `widget-voice-name`.
- The window itself is defined in [Rust window commands](rust-window-commands.md).

## Related

- [Tauri events and channels](../interfaces/tauri-events.md)
- [Route shell](route-shell.md)
