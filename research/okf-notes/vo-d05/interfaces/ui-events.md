---
id: interfaces/ui-events
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Window events
description: Events exchanged between the widget window and the main window, plus the Tauri window layout.
domain: architecture
tags:
  - interface
  - events
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/widget/+page.svelte
  - resource: src-tauri/src/commands/window.rs
  - resource: src-tauri/tauri.conf.json
  - resource: src-tauri/capabilities/default.json
related:
  - interfaces/tauri-commands
  - building-blocks/frontend-routes
  - building-blocks/tauri-recording
---

# Window events

The widget window sends events with names below.

## Facts

- `recording-pause` and `recording-resume`: emitted by `handlePause` through `plugin:event|emit` (src/routes/widget/+page.svelte).
- `recording-stop` and `recording-cancel`: emitted with `emit`, then `close_widget_window` is invoked.
- `widget-voice-name`: listened to by the widget; payload is a string shown as `voiceName`.
- Windows: main window label `main`, 480x640, title VoiceOver (src-tauri/tauri.conf.json); `widget` is created by `create_widget_window` (src-tauri/src/commands/window.rs).
- The capability file lists `main` and `widget` (src-tauri/capabilities/default.json).

## Related

- [[interfaces/tauri-commands]] - Tauri commands
- [[building-blocks/frontend-routes]] - Frontend routes
- [[building-blocks/tauri-recording]] - Rust recording commands
