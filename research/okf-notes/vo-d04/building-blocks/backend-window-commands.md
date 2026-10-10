---
id: building-blocks/backend-window-commands
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Backend window commands"
description: "Commands that open and close the widget window."
domain: architecture
tags:
  - backend
  - commands
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
architecture_layer: building-blocks
sources:
  - resource: src-tauri/src/commands/window.rs
related:
  - building-blocks/route-widget
  - runtime/widget-window-flow
  - interfaces/tauri-commands
---

# Backend window commands

`src-tauri/src/commands/window.rs` manages the window labelled `widget`.

## Facts (src-tauri/src/commands/window.rs)
- `create_widget_window(app)`: returns Ok if a `widget` window exists; otherwise builds one at `WebviewUrl::App("/widget")`, title "Recording", inner size 340 by 80, not resizable, no decorations, always on top, centered.
- `close_widget_window(app)`: closes the `widget` window if present.

## Callers
`close_widget_window` is invoked from src/routes/widget/+page.svelte. No call to `create_widget_window` appears under src/.

## Related

- [[building-blocks/route-widget]]
- [[runtime/widget-window-flow]]
- [[interfaces/tauri-commands]]
