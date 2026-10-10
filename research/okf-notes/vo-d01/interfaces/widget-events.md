---
id: interfaces/widget-events
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Widget Events"
description: "Event names used between the widget window and the rest of the app."
domain: architecture
tags:
  - interface
  - events
  - widget
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/widget/+page.svelte
---
# Widget Events

The widget page uses the Tauri event API.

## Facts
- Listens: `widget-voice-name`, payload string (`listen` in onMount).
- Emits: `recording-pause`, `recording-resume` (through `invoke('plugin:event|emit', ...)` with payload null), `recording-stop`, `recording-cancel` (through `emit`).
- Commands used with them: `close_widget_window`.

## Related
- [[building-blocks/widget-screen]]
- [[runtime/widget-controls]]
- [[interfaces/tauri-commands]]
