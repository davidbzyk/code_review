---
id: runtime/widget-window-flow
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Widget window flow"
description: "Events and commands used by the recording widget page."
domain: architecture
tags:
  - runtime
  - widget
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
architecture_layer: runtime
sources:
  - resource: src/routes/widget/+page.svelte
  - resource: src-tauri/src/commands/window.rs
  - resource: src-tauri/tauri.conf.json
related:
  - building-blocks/route-widget
  - building-blocks/backend-window-commands
  - interfaces/window-events
---

# Widget window flow

The widget page emits control events and closes its own window.

## Steps
1. `create_widget_window` builds the `widget` window at `/widget` (src-tauri/src/commands/window.rs).
2. The page starts its interval and subscribes to `widget-voice-name` (src/routes/widget/+page.svelte).
3. Pause toggles `isPaused` and emits `recording-pause` or `recording-resume`.
4. Stop clears the interval, emits `recording-stop`, invokes `close_widget_window`.
5. Cancel emits `recording-cancel`, invokes `close_widget_window`.
6. `close_widget_window` closes the window labelled `widget` (src-tauri/src/commands/window.rs).

## Notes
The capability file lists windows `main` and `widget` (src-tauri/capabilities/default.json). The names `recording-stop`, `recording-cancel`, `recording-pause`, `recording-resume` and `widget-voice-name` appear only in src/routes/widget/+page.svelte.

## Related

- [[building-blocks/route-widget]]
- [[building-blocks/backend-window-commands]]
- [[interfaces/window-events]]
