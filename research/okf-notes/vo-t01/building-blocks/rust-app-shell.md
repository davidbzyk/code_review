---
id: building-blocks/rust-app-shell
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Rust App Shell
description: Tauri builder, plugin setup, startup tasks and small helper modules.
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
  - resource: src-tauri/src/prerequisites.rs
  - resource: src-tauri/src/tts_provider.rs
relations:
  relates_to:
    - runtime/sidecar-startup
    - interfaces/tauri-commands-app
    - building-blocks/rust-local-tts-and-sidecar
    - building-blocks/rust-recording-and-library
---
# Rust App Shell

The shell builds the Tauri app, registers every command, and starts background work.

## Files

- `main.rs`: `fn main` calls `voiceover_lib::run()`.
- `build.rs`: calls `tauri_build::build()`.
- `lib.rs`: `run()` adds the shell, dialog, fs and global-shortcut plugins; in `setup` it adds `tauri_plugin_log` at `Info`, calls `prerequisites::check_ffmpeg`, manages `SidecarState` and `HttpClient`, calls `cleanup_stale_recordings` with 3600 seconds, and spawns `sidecar::start_sidecar`. It lists commands in `generate_handler!`.
- `commands/mod.rs` declares `recording` and `window`.
- `commands/window.rs`: `create_widget_window` opens a 340 by 80 always-on-top window at `/widget`; `close_widget_window` closes it.
- `prerequisites.rs`: `check_ffmpeg`, command `check_prerequisites` returning `PrerequisiteStatus`.
- `tts_provider.rs`: enum `Provider` with `ElevenLabs` and `Local`, serialized as lowercase.

## Uses

`config`, `elevenlabs`, `ffmpeg`, `google_drive`, `library`, `local_tts`, `models`, `pipeline`, `secrets`, `sidecar`.

## Related

- [Flow: Sidecar Startup and Health](../runtime/sidecar-startup.md)
- [Tauri Commands: Config, Recording, Library, Drive, Window](../interfaces/tauri-commands-app.md)
- [Rust Local TTS and Sidecar Manager](rust-local-tts-and-sidecar.md)
- [Rust Recording and Library](rust-recording-and-library.md)
