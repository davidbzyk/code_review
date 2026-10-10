---
id: building-blocks/backend-shell
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Backend shell"
description: "Rust entry point that builds the Tauri app and registers plugins and commands."
domain: architecture
tags:
  - backend
  - tauri
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
architecture_layer: building-blocks
sources:
  - resource: src-tauri/src/lib.rs
  - resource: src-tauri/src/main.rs
  - resource: src-tauri/build.rs
  - resource: src-tauri/src/commands/mod.rs
related:
  - interfaces/tauri-commands
  - building-blocks/backend-config
  - building-blocks/backend-pipeline
  - building-blocks/backend-recording-commands
  - building-blocks/backend-window-commands
  - building-blocks/backend-google-drive
  - building-blocks/backend-ffmpeg
---

# Backend shell

`run()` in `src-tauri/src/lib.rs` builds the Tauri application.

## Facts
- `main()` calls `voiceover_lib::run()` (src-tauri/src/main.rs).
- `run()` registers plugins shell, dialog, fs and global-shortcut (src-tauri/src/lib.rs).
- In `setup`, a debug build adds `tauri_plugin_log` at level Info, and `prerequisites::check_ffmpeg()` logs an error when ffmpeg is missing (src-tauri/src/lib.rs).
- `invoke_handler` lists 14 commands (src-tauri/src/lib.rs); see [[interfaces/tauri-commands]].
- Modules declared: `commands`, `config`, `elevenlabs`, `ffmpeg`, `google_drive`, `pipeline`, `prerequisites` (src-tauri/src/lib.rs).
- `commands/mod.rs` declares `pub mod recording` and `pub mod window` (src-tauri/src/commands/mod.rs).
- `build.rs` calls `tauri_build::build()` (src-tauri/build.rs).

## Calls
All other backend blocks.

## Related

- [[interfaces/tauri-commands]]
- [[building-blocks/backend-config]]
- [[building-blocks/backend-pipeline]]
- [[building-blocks/backend-recording-commands]]
- [[building-blocks/backend-window-commands]]
- [[building-blocks/backend-google-drive]]
- [[building-blocks/backend-ffmpeg]]
