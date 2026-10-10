---
id: building-blocks/rust-window-commands
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Rust Window Commands"
description: "Commands that open and close the small always-on-top recording widget window."
domain: architecture
tags:
  - building-blocks
  - rust
  - window
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/commands/window.rs
  - resource: src-tauri/capabilities/default.json
relations:
  relates_to:
    - building-blocks/route-widget
    - building-blocks/rust-app-shell
    - interfaces/tauri-commands-core
---

The window module creates and closes the webview window labelled `widget`.

## Facts

- `create_widget_window(app)` returns early when `app.get_webview_window("widget")` exists (`src-tauri/src/commands/window.rs`).
- Otherwise it builds a `WebviewWindowBuilder` with label `widget`, url `WebviewUrl::App("/widget")`, title "Recording", inner size 340 by 80, not resizable, no decorations, always on top, centered (`src-tauri/src/commands/window.rs`).
- `close_widget_window(app)` closes the window labelled `widget` when it exists.
- `src-tauri/capabilities/default.json` lists `main` and `widget` under `windows`, plus permissions such as `core:window:allow-create` and `core:webview:allow-create-webview-window`.
- In `src/` the only call site is `invoke('close_widget_window')` in the widget route; `create_widget_window` has no call site in `src/`.

## Related

- [Widget route](route-widget.md)
- [Rust app shell](rust-app-shell.md)
- [Tauri commands, core](../interfaces/tauri-commands-core.md)
