---
id: building-blocks/window-commands
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Window Commands"
description: "Backend commands that create and close the floating recording widget window."
domain: architecture
tags:
  - building-block
  - rust
  - window
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/commands/window.rs
  - resource: src-tauri/capabilities/default.json
---
# Window Commands

`window.rs` manages the second webview window labelled `widget`.

## Facts
- `create_widget_window` returns early if a window labelled `widget` exists; otherwise it builds one with `WebviewWindowBuilder` at `WebviewUrl::App("/widget")`, size 340 by 80, not resizable, no decorations, transparent, always on top, centered.
- `close_widget_window` closes the `widget` window if present.
- Capabilities list the windows `main` and `widget` (src-tauri/capabilities/default.json).

## Called by
`handleRecord` in src/routes/+page.svelte; `handleStop` and `handleCancel` in src/routes/widget/+page.svelte.

## Related
- [[building-blocks/widget-screen]]
- [[runtime/widget-controls]]
- [[interfaces/tauri-commands]]
