---
id: runtime/startup
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Application Startup"
description: "Steps from launching the desktop binary to a loaded main window."
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
---
# Application Startup

Startup runs a Rust setup step and then a frontend mount step.

## Steps
1. `main` calls `voiceover_lib::run()` (src-tauri/src/main.rs).
2. `run` builds `tauri::Builder` and registers the four plugins (src-tauri/src/lib.rs).
3. The `setup` closure adds the log plugin in debug builds and calls `prerequisites::check_ffmpeg()` (src-tauri/src/prerequisites.rs).
4. The `main` window from src-tauri/tauri.conf.json loads the built frontend.
5. `onMount` in src/routes/+layout.svelte calls `appState.loadConfig()` (src/lib/state.svelte.ts), which invokes `get_config`.
6. In Tauri the layout invokes `check_prerequisites` and sets `appState.ffmpegAvailable`.

## Related
- [[building-blocks/tauri-shell]]
- [[building-blocks/frontend-shell]]
- [[runtime/config-load-and-save]]
