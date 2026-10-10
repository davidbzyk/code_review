---
id: building-blocks/rust-app-shell
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Rust app shell"
description: "lib.rs builds the Tauri app, registers plugins and every command, and main.rs only calls run()."
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
  - resource: src-tauri/src/commands/mod.rs
  - resource: src-tauri/src/commands/window.rs
  - resource: src-tauri/capabilities/default.json
relations:
  relates_to:
    - interfaces/tauri-commands
    - runtime/app-startup
    - building-blocks/rust-recording-commands
---
# Rust app shell

The shell is the entry point of the Rust crate `voiceover_lib`.

## Files

- src-tauri/src/main.rs: `main()` calls `voiceover_lib::run()`; on Windows release builds it sets `windows_subsystem = "windows"`.
- src-tauri/build.rs: `main()` calls `tauri_build::build()`.
- src-tauri/src/lib.rs: declares modules `commands`, `config`, `elevenlabs`, `ffmpeg`, `google_drive`, `pipeline`, `prerequisites`. `run()` adds the shell, dialog, fs and global-shortcut plugins, adds the log plugin in debug builds, logs an error if `prerequisites::check_ffmpeg()` is false, and registers 14 commands with `tauri::generate_handler!`.
- src-tauri/src/commands/mod.rs: declares `recording` and `window`.
- src-tauri/src/commands/window.rs: `create_widget_window` opens a 340 by 80 undecorated, always-on-top window labelled `widget` at URL `/widget`, and returns early if one exists; `close_widget_window` closes it.
- src-tauri/capabilities/default.json: permission set for windows `main` and `widget`, including ffmpeg shell execution scopes.

## Related

[[interfaces/tauri-commands]], [[runtime/app-startup]], [[building-blocks/rust-recording-commands]]
