---
id: building-blocks/tauri-core
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Tauri core
description: The Rust entry point registers plugins, startup tasks and every command handler.
domain: architecture
tags:
  - building-block
  - rust
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/main.rs
  - resource: src-tauri/src/lib.rs
  - resource: src-tauri/build.rs
  - resource: src-tauri/src/prerequisites.rs
  - resource: src-tauri/src/tts_provider.rs
  - resource: src-tauri/capabilities/default.json
  - resource: src-tauri/src/commands/mod.rs
related:
  - interfaces/tauri-commands
  - runtime/sidecar-startup
  - building-blocks/tauri-recording
---

# Tauri core

`main.rs` calls `voiceover_lib::run()`; `run()` in `lib.rs` builds the Tauri app.

## Facts

- `run()` registers plugins: shell, dialog, fs, global-shortcut, and log (level Info) (src-tauri/src/lib.rs).
- Setup checks `prerequisites::check_ffmpeg()`, manages `sidecar::SidecarState`, calls `cleanup_stale_recordings` with a 3600 s age, and spawns `sidecar::start_sidecar`.
- `generate_handler!` lists the commands in [[interfaces/tauri-commands]].
- `build.rs` calls `tauri_build::build()`.
- `prerequisites.rs`: `check_ffmpeg()` runs `ffmpeg -version`; command `check_prerequisites` returns `PrerequisiteStatus { ffmpeg_available, ffmpeg_version }`.
- `tts_provider.rs` defines enum `Provider` with `ElevenLabs` and `Local` and `as_str()`.
- `commands/mod.rs` declares `recording` and `window` modules.
- `capabilities/default.json` grants windows `main` and `widget` the window, shell, dialog, fs and global-shortcut permissions, and allows the sidecars `binaries/ffmpeg` and `binaries/voiceover-tts`.

## Uses

- Calls the modules in [[building-blocks/tauri-recording]], [[building-blocks/tauri-config-secrets]], [[building-blocks/tauri-media-pipeline]], [[building-blocks/tauri-local-tts-bridge]] and [[building-blocks/tauri-google-drive]].

## Related

- [[interfaces/tauri-commands]] - Tauri commands
- [[runtime/sidecar-startup]] - Sidecar startup
- [[building-blocks/tauri-recording]] - Rust recording commands
