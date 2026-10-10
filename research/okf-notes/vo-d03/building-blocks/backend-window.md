---
id: building-blocks/backend-window
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Backend window commands"
description: "Commands that open and close the floating widget window."
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
relations:
  relates_to:
    - building-blocks/page-widget
    - interfaces/tauri-commands
---

# Backend window commands

`src-tauri/src/commands/window.rs` manages the Tauri window labelled `widget`.

## Functions

- `create_widget_window(app)` (async command): returns early if a `widget` window exists; otherwise builds a `WebviewWindowBuilder` with URL `WebviewUrl::App("/widget")`, title `Recording`, inner size 340 by 80, not resizable, no decorations, always on top, centered.
- `close_widget_window(app)` (async command): closes the `widget` window when present.

## Called by

`close_widget_window` is invoked from `src/routes/widget/+page.svelte`. Both commands are registered in `src-tauri/src/lib.rs`.

## Related

- [building-blocks/page-widget](./page-widget.md)
- [interfaces/tauri-commands](../interfaces/tauri-commands.md)
- [building-blocks/backend-entry](./backend-entry.md)
