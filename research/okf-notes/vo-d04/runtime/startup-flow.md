---
id: runtime/startup-flow
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Startup flow"
description: "What runs when the desktop app and the root layout start."
domain: architecture
tags:
  - runtime
  - startup
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
architecture_layer: runtime
sources:
  - resource: src-tauri/src/main.rs
  - resource: src-tauri/src/lib.rs
  - resource: src-tauri/src/prerequisites.rs
  - resource: src/routes/+layout.svelte
  - resource: src/lib/state.svelte.ts
related:
  - runtime/config-load-save-flow
  - building-blocks/backend-shell
  - building-blocks/frontend-shell
---

# Startup flow

The Rust process starts first, then the webview loads the layout, which loads config and checks ffmpeg.

## Steps
1. `main()` calls `voiceover_lib::run()` (src-tauri/src/main.rs).
2. `run()` creates `tauri::Builder::default()` and adds the plugins (src-tauri/src/lib.rs).
3. `setup` adds the log plugin in debug builds and calls `prerequisites::check_ffmpeg()` (src-tauri/src/lib.rs, src-tauri/src/prerequisites.rs).
4. `generate_handler!` registers the commands and `.run(generate_context!())` opens the window (src-tauri/src/lib.rs).
5. The webview renders `+layout.svelte`; `onMount` awaits `appState.loadConfig()` (src/routes/+layout.svelte, src/lib/state.svelte.ts).
6. In Tauri, `invoke('check_prerequisites')` sets `appState.ffmpegAvailable` (src/routes/+layout.svelte).

## Related

- [[runtime/config-load-save-flow]]
- [[building-blocks/backend-shell]]
- [[building-blocks/frontend-shell]]
