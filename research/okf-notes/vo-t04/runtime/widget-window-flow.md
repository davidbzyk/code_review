---
id: runtime/widget-window-flow
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Recording widget flow"
description: "The widget route shows a timer and sends pause, stop and cancel events; the Rust side creates and closes its window."
domain: architecture
tags:
  - runtime
  - widget
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/widget/+page.svelte
  - resource: src-tauri/src/commands/window.rs
relations:
  relates_to:
    - building-blocks/frontend-pages
    - building-blocks/rust-app-shell
    - interfaces/tauri-events-and-channels
---
# Recording widget flow

The widget is a second window labelled `widget` that loads the `/widget` route.

## Steps

1. `create_widget_window` builds a `WebviewWindowBuilder` for label `widget` with URL `/widget` unless it exists (src-tauri/src/commands/window.rs). No call to it appears in src.
2. On mount, the widget page returns early outside Tauri; inside Tauri it starts a one-second timer that increments `duration` while not paused (src/routes/widget/+page.svelte).
3. It listens for the event `widget-voice-name` and stores the payload in `voiceName`.
4. `handlePause()` toggles `isPaused` and invokes `plugin:event|emit` with `recording-pause` or `recording-resume`.
5. `handleStop()` clears the timer, emits `recording-stop`, then invokes `close_widget_window`.
6. `handleCancel()` emits `recording-cancel`, then invokes `close_widget_window`.
7. `close_widget_window` closes the window if present.

## Related

[[building-blocks/frontend-pages]], [[building-blocks/rust-app-shell]], [[interfaces/tauri-events-and-channels]]
