---
id: runtime/widget-controls
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Widget Controls"
description: "Lifecycle of the floating widget window during a recording."
domain: architecture
tags:
  - runtime
  - widget
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/+page.svelte
  - resource: src/routes/widget/+page.svelte
  - resource: src-tauri/src/commands/window.rs
---
# Widget Controls

The widget window is created when recording starts and closed from its own buttons.

## Steps
1. `handleRecord` invokes `create_widget_window` (src/routes/+page.svelte).
2. `create_widget_window` builds a window labelled `widget` at `/widget` (src-tauri/src/commands/window.rs).
3. The widget page starts a one-second timer in `onMount` (src/routes/widget/+page.svelte).
4. Pause button: `handlePause` emits `recording-pause` or `recording-resume`.
5. Stop button: `handleStop` emits `recording-stop`, then invokes `close_widget_window`.
6. Cancel button: `handleCancel` emits `recording-cancel`, then `close_widget_window`.

## Related
- [[building-blocks/widget-screen]]
- [[building-blocks/window-commands]]
- [[interfaces/widget-events]]
