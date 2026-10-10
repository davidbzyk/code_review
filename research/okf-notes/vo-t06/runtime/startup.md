---
id: runtime/startup
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Application Startup"
description: "What happens from process start to the first rendered screen."
domain: architecture
tags:
  - runtime
  - startup
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/main.rs
  - resource: src-tauri/src/lib.rs
  - resource: src/routes/+layout.svelte
  - resource: src-tauri/tauri.conf.json
relations:
  relates_to:
    - runtime/config-load-save
    - building-blocks/rust-app-shell
    - building-blocks/route-shell
---

The desktop process starts Rust, opens the `main` window and loads the SvelteKit app.

## Steps

1. `main()` in `src-tauri/src/main.rs` calls `voiceover_lib::run()`.
2. `run()` in `src-tauri/src/lib.rs` builds the Tauri app, adds plugins and registers command handlers.
3. The `setup` closure adds `tauri_plugin_log` in debug builds and calls `prerequisites::check_ffmpeg()`; it logs an error when ffmpeg is missing.
4. Tauri opens the window labelled `main` (title "VoiceOver", 480 by 640) from `app.windows` in `src-tauri/tauri.conf.json`.
5. The webview loads `devUrl` `http://localhost:5170` in development or `frontendDist` `../build` in a packaged app.
6. `src/routes/+layout.svelte` runs `appState.loadConfig()` on mount.
7. When `isTauri()` is true, the layout invokes `check_prerequisites` and sets `appState.ffmpegAvailable`.
8. The route `/` (`src/routes/+page.svelte`) renders the record screen.

## Related

- [Config load and save flow](config-load-save.md)
- [Rust app shell](../building-blocks/rust-app-shell.md)
- [Route shell](../building-blocks/route-shell.md)
