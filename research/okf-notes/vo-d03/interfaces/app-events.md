---
id: interfaces/app-events
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Window events"
description: "Tauri events the widget window emits or listens for."
domain: architecture
tags:
  - interface
  - tauri
  - events
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/widget/+page.svelte
  - resource: src-tauri/src/commands/window.rs
relations:
  relates_to:
    - building-blocks/page-widget
    - building-blocks/backend-window
---

# Window events

The widget page uses Tauri's event API to talk to other windows.

| Event | Direction | Payload | Code |
|---|---|---|---|
| `widget-voice-name` | listened by widget | string stored as `voiceName` | `onMount` in `src/routes/widget/+page.svelte` |
| `recording-pause` | emitted by widget | null | `handlePause()` |
| `recording-resume` | emitted by widget | null | `handlePause()` |
| `recording-stop` | emitted by widget | none | `handleStop()` |
| `recording-cancel` | emitted by widget | none | `handleCancel()` |

`recording-pause` and `recording-resume` are sent with `invoke('plugin:event|emit', ...)`; `recording-stop` and `recording-cancel` use `emit` from `@tauri-apps/api/event`.

No other file in `src/` calls `listen` or emits these names. The widget window itself is defined by `create_widget_window` in `src-tauri/src/commands/window.rs`.

## Related

- [building-blocks/page-widget](../building-blocks/page-widget.md)
- [building-blocks/backend-window](../building-blocks/backend-window.md)
- [interfaces/tauri-commands](./tauri-commands.md)
