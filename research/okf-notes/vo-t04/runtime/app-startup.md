---
id: runtime/app-startup
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "App startup flow"
description: "On launch the Rust side builds the Tauri app and the root layout loads config and checks ffmpeg."
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
  - resource: src-tauri/src/prerequisites.rs
  - resource: src/routes/+layout.svelte
  - resource: src/lib/state.svelte.ts
relations:
  relates_to:
    - building-blocks/rust-app-shell
    - building-blocks/frontend-shell
    - runtime/config-load-and-save
---
# App startup flow

Startup runs a Rust phase and then a frontend phase.

## Steps

1. `main()` calls `voiceover_lib::run()` (src-tauri/src/main.rs).
2. `run()` creates `tauri::Builder::default()` and adds the shell, dialog, fs and global-shortcut plugins (src-tauri/src/lib.rs).
3. In `setup`, debug builds add `tauri_plugin_log` at level Info (src-tauri/src/lib.rs).
4. `setup` calls `prerequisites::check_ffmpeg()` and logs an error when it returns false (src-tauri/src/prerequisites.rs).
5. `run()` registers the command list and calls `generate_context!()` to start the app (src-tauri/src/lib.rs).
6. The webview loads the SvelteKit app; `onMount` in src/routes/+layout.svelte awaits `appState.loadConfig()` (src/lib/state.svelte.ts).
7. If `isTauri()`, the layout invokes `check_prerequisites` and assigns `ffmpeg_available` to `appState.ffmpegAvailable`; a failure is logged with `console.error`.
8. The layout shows the ffmpeg banner while `appState.ffmpegAvailable` is false.

## Related

[[building-blocks/rust-app-shell]], [[building-blocks/frontend-shell]], [[runtime/config-load-and-save]]
