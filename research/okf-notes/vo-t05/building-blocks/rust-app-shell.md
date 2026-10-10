---
id: building-blocks/rust-app-shell
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Rust App Shell
description: The Tauri entry point that registers plugins, shared state, startup tasks and every command.
domain: architecture
tags:
  - building-block
  - rust
  - tauri
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/lib.rs
  - resource: src-tauri/src/main.rs
  - resource: src-tauri/build.rs
  - resource: src-tauri/src/prerequisites.rs
  - resource: src-tauri/src/commands/mod.rs
  - resource: src-tauri/src/commands/window.rs
  - resource: src-tauri/capabilities/default.json
related:
  - interfaces/commands-app-config-recording
  - runtime/sidecar-startup
  - building-blocks/rust-sidecar-manager
  - crosscutting/security-boundaries
---

# Rust App Shell

`run()` in lib.rs builds the Tauri app; `main.rs` only calls `voiceover_lib::run()`.

## Facts

- Plugins: shell, dialog, fs, global-shortcut, and log at level Info (src-tauri/src/lib.rs).
- `setup` calls `prerequisites::check_ffmpeg`, manages `sidecar::SidecarState` and `local_tts::HttpClient` (pool_max_idle_per_host 5), calls `cleanup_stale_recordings` with 3600 s, and spawns `sidecar::start_sidecar` in the background.
- `tauri::generate_handler!` registers 26 commands from `prerequisites`, `config`, `recording`, `window`, `pipeline`, `elevenlabs`, `local_tts`, `sidecar`, `models` and `google_drive`.
- `check_prerequisites` returns `PrerequisiteStatus { ffmpeg_available, ffmpeg_version }` (src-tauri/src/prerequisites.rs).
- `create_widget_window` opens webview label `widget` at `/widget`, 340 by 80, no decorations, always on top; `close_widget_window` closes it (src-tauri/src/commands/window.rs).
- `build.rs` calls `tauri_build::build()`.
- Capability `default` applies to windows `main` and `widget` (src-tauri/capabilities/default.json).
- `commands/mod.rs` declares `recording` and `window`.

## Calls

All other Rust modules.

## Related

- [Tauri Commands: App, Config, Recording](../interfaces/commands-app-config-recording.md)
- [Flow: Sidecar Startup and Shutdown](../runtime/sidecar-startup.md)
- [Rust Sidecar Manager](./rust-sidecar-manager.md)
- [Security Boundaries](../crosscutting/security-boundaries.md)
