---
id: building-blocks/backend-window-commands
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Rust window commands
description: Commands that open and close the floating recording widget window.
domain: architecture
tags:
  - building-block
  - backend
  - window
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/commands/window.rs
related:
  - building-blocks/frontend-record-page
  - interfaces/tauri-commands
---

src-tauri/src/commands/window.rs creates and closes the `widget` webview window.

## Functions
- `create_widget_window(app)`: returns Ok when a `widget` window exists; otherwise builds one with `WebviewWindowBuilder` at `WebviewUrl::App("/widget")`, title "Recording", inner size 340 by 80, not resizable, no decorations, always on top, centered.
- `close_widget_window(app)`: closes the `widget` window if present.

## Called by
src/routes/+page.svelte (`create_widget_window`) and src/routes/widget/+page.svelte (`close_widget_window`).

## Related
[[building-blocks/frontend-record-page]], [[interfaces/tauri-commands]]
