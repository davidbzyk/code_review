---
id: building-blocks/tauri-host
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Tauri host entry and window commands"
description: "The Rust crate entry, plugin setup, command registration, widget window commands and the ffmpeg prerequisite check."
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
  - resource: src-tauri/build.rs
  - resource: src-tauri/src/commands/mod.rs
  - resource: src-tauri/src/commands/window.rs
  - resource: src-tauri/src/prerequisites.rs
  - resource: src-tauri/src/tts_provider.rs
  - resource: src-tauri/capabilities/default.json
related:
  - interfaces/tauri-commands
  - building-blocks/rust-config-and-secrets
  - building-blocks/rust-pipeline
  - building-blocks/rust-sidecar-client
  - building-blocks/rust-google-drive
  - building-blocks/rust-recording-files
  - runtime/sidecar-startup
  - deployment/build-and-run
---
# Tauri host entry and window commands

The host builds the Tauri app, registers every command and starts the sidecar in the background.

## Facts

- `main.rs` calls `voiceover_lib::run()`; `build.rs` calls `tauri_build::build()`.
- `run()` in `lib.rs` adds the shell, dialog, fs and global-shortcut plugins, then in `setup` adds the log plugin at `Info`, calls `prerequisites::check_ffmpeg()`, manages `sidecar::SidecarState` and spawns `sidecar::start_sidecar`.
- `generate_handler!` registers the commands listed in [[interfaces/tauri-commands]].
- `commands/mod.rs` declares modules `recording` and `window`.
- `window.rs`: `create_widget_window` builds a 340 by 80 undecorated, always-on-top window labelled `widget` at `/widget`; `close_widget_window` closes it.
- `prerequisites.rs`: `check_ffmpeg` runs `ffmpeg -version`; command `check_prerequisites` returns `PrerequisiteStatus { ffmpeg_available, ffmpeg_version }`.
- `tts_provider.rs`: enum `Provider` (`ElevenLabs`, `Local`) with `as_str`, marked `allow(dead_code)`.
- `capabilities/default.json` grants window, shell sidecar, dialog, fs and global-shortcut permissions to windows `main` and `widget`.

## Calls

[[building-blocks/rust-config-and-secrets]], [[building-blocks/rust-pipeline]], [[building-blocks/rust-sidecar-client]], [[building-blocks/rust-google-drive]], [[building-blocks/rust-recording-files]].

## Related

- [[runtime/sidecar-startup]]
- [[deployment/build-and-run]]
