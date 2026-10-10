---
id: building-blocks/rust-app-shell
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Rust App Shell"
description: "The Tauri entry point that registers plugins and the command handlers."
domain: architecture
tags:
  - building-blocks
  - rust
  - tauri
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/lib.rs
  - resource: src-tauri/src/main.rs
  - resource: src-tauri/src/commands/mod.rs
  - resource: src-tauri/build.rs
relations:
  relates_to:
    - building-blocks/rust-recording-commands
    - building-blocks/rust-window-commands
    - deployment/build-and-package
    - interfaces/tauri-commands-core
    - interfaces/tauri-commands-services
---

The Rust shell builds the Tauri application, loads four plugins and exposes fourteen commands to the webview.

## Facts

- `main` in `src-tauri/src/main.rs` calls `voiceover_lib::run()`; the crate name comes from `[lib]` in `src-tauri/Cargo.toml`.
- `run()` in `src-tauri/src/lib.rs` declares the modules `commands`, `config`, `elevenlabs`, `ffmpeg`, `google_drive`, `pipeline`, `prerequisites`, `secrets` (`src-tauri/src/lib.rs`).
- Plugins added: `tauri_plugin_shell`, `tauri_plugin_dialog`, `tauri_plugin_fs`, `tauri_plugin_global_shortcut` (`src-tauri/src/lib.rs`).
- The `setup` closure adds `tauri_plugin_log` only when `cfg!(debug_assertions)` is true, then calls `prerequisites::check_ffmpeg()` and logs an error when it returns false (`src-tauri/src/lib.rs`).
- `tauri::generate_handler!` lists the commands; the full list is in [Tauri commands, core](../interfaces/tauri-commands-core.md) and [Tauri commands, services](../interfaces/tauri-commands-services.md).
- `src-tauri/src/commands/mod.rs` declares `pub mod recording;` and `pub mod window;`.
- `src-tauri/build.rs` calls `tauri_build::build()`.

## Related

- [Recording commands](rust-recording-commands.md)
- [Window commands](rust-window-commands.md)
- [Build and package](../deployment/build-and-package.md)
