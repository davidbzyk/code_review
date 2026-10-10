---
id: building-blocks/backend-entry
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Backend entry and app builder"
description: "Rust binary entry, library run function, plugin setup and command registration."
domain: architecture
tags:
  - building-block
  - backend
  - tauri
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/main.rs
  - resource: src-tauri/src/lib.rs
  - resource: src-tauri/build.rs
  - resource: src-tauri/capabilities/default.json
relations:
  relates_to:
    - interfaces/tauri-commands
    - deployment/build-and-packaging
    - crosscutting/permissions-and-csp
---

# Backend entry and app builder

The Rust side starts in `main.rs`, builds the Tauri app in `lib.rs`, and registers every command.

## Facts

- `src-tauri/src/main.rs`: `fn main` calls `voiceover_lib::run()`; `windows_subsystem = "windows"` applies when `debug_assertions` is off.
- `src-tauri/build.rs`: `fn main` calls `tauri_build::build()`.
- `src-tauri/src/lib.rs` declares modules `commands`, `config`, `elevenlabs`, `ffmpeg`, `google_drive`, `pipeline`, `prerequisites`.
- `pub fn run()` builds `tauri::Builder::default()` with plugins shell, dialog, fs and global-shortcut.
- The `setup` closure adds `tauri_plugin_log` at level Info when `cfg!(debug_assertions)`, then calls `prerequisites::check_ffmpeg()` and logs an error if it fails.
- `invoke_handler` registers 14 commands (listed in [tauri-commands](../interfaces/tauri-commands.md)).
- `src-tauri/capabilities/default.json`: capability `default` for windows `main` and `widget`, with core window, dialog, fs, shell `ffmpeg` execute and global-shortcut permissions.

## Calls

[backend-config](./backend-config.md), [backend-recording](./backend-recording.md), [backend-window](./backend-window.md), [backend-pipeline](./backend-pipeline.md), [backend-ffmpeg](./backend-ffmpeg.md), [backend-elevenlabs](./backend-elevenlabs.md), [backend-google-drive](./backend-google-drive.md).

## Related

- [interfaces/tauri-commands](../interfaces/tauri-commands.md)
- [deployment/build-and-packaging](../deployment/build-and-packaging.md)
- [crosscutting/permissions-and-csp](../crosscutting/permissions-and-csp.md)
