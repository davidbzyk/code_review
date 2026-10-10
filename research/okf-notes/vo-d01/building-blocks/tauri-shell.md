---
id: building-blocks/tauri-shell
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Tauri Shell"
description: "The Rust entry module that registers plugins and every command handler."
domain: architecture
tags:
  - building-block
  - rust
  - tauri
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/main.rs
  - resource: src-tauri/src/lib.rs
  - resource: src-tauri/src/commands/mod.rs
  - resource: src-tauri/build.rs
---
# Tauri Shell

The shell builds the Tauri application, loads plugins and exposes the command list to the frontend.

## Facts
- `main` in src-tauri/src/main.rs only calls `voiceover_lib::run()`.
- `run` in src-tauri/src/lib.rs declares the modules `commands`, `config`, `elevenlabs`, `ffmpeg`, `google_drive`, `pipeline`, `prerequisites`.
- It registers plugins `tauri_plugin_shell`, `tauri_plugin_dialog`, `tauri_plugin_fs`, `tauri_plugin_global_shortcut` (src-tauri/src/lib.rs).
- In debug builds the `setup` closure adds `tauri_plugin_log` at level Info, then calls `prerequisites::check_ffmpeg()` and logs an error if it fails.
- `tauri::generate_handler!` lists the 13 commands (see [[interfaces/tauri-commands]]).
- src-tauri/src/commands/mod.rs declares `pub mod recording` and `pub mod window`.
- src-tauri/build.rs calls `tauri_build::build()`.

## Calls
`config`, `prerequisites`, `pipeline`, `elevenlabs`, `google_drive`, `commands::recording`, `commands::window`.

## Related
- [[building-blocks/config-store]]
- [[building-blocks/media-pipeline]]
- [[building-blocks/recording-commands]]
- [[building-blocks/window-commands]]
- [[building-blocks/elevenlabs-client]]
- [[building-blocks/google-drive-backend]]
