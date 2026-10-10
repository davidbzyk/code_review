---
id: building-blocks/backend-entry
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Rust entry and command registry
description: main.rs, lib.rs and the Tauri builder that registers plugins and every command.
domain: architecture
tags:
  - building-block
  - backend
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/main.rs
  - resource: src-tauri/src/lib.rs
  - resource: src-tauri/build.rs
related:
  - interfaces/tauri-commands
  - building-blocks/backend-prerequisites
  - deployment/build-and-packaging
---

`run()` in src-tauri/src/lib.rs builds the Tauri application; `main()` in src-tauri/src/main.rs only calls `voiceover_lib::run()`.

## Facts
- src-tauri/src/main.rs sets `windows_subsystem = "windows"` for release builds.
- src-tauri/src/lib.rs declares modules `commands`, `config`, `elevenlabs`, `ffmpeg`, `google_drive`, `pipeline`, `prerequisites`.
- Plugins: `tauri_plugin_shell`, `tauri_plugin_dialog`, `tauri_plugin_fs`, `tauri_plugin_global_shortcut`; `tauri_plugin_log` only when `debug_assertions` is on, at level Info.
- In `setup`, `prerequisites::check_ffmpeg()` runs and logs an error when false.
- `invoke_handler` registers the thirteen commands listed in [[interfaces/tauri-commands]].
- src-tauri/build.rs calls `tauri_build::build()`.

## Related
[[interfaces/tauri-commands]], [[building-blocks/backend-prerequisites]], [[deployment/build-and-packaging]]
