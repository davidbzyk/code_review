---
id: building-blocks/backend-entry-and-commands
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Backend Entry and Commands"
description: "The Rust entry point, plugin setup, handler registration, recording commands, window commands and the ffmpeg check."
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
  - resource: src-tauri/src/commands/mod.rs
  - resource: src-tauri/src/commands/recording.rs
  - resource: src-tauri/src/commands/window.rs
  - resource: src-tauri/src/prerequisites.rs
  - resource: src-tauri/build.rs
related:
  - building-blocks/backend-pipeline-and-ffmpeg
  - interfaces/tauri-commands-recording-and-pipeline
  - crosscutting/security-boundaries
---
# Backend Entry and Commands

This block starts the Tauri app and exposes file and window commands.

## Files
- src-tauri/src/main.rs: calls `voiceover_lib::run()`.
- src-tauri/src/lib.rs: `run` builds the app with plugins shell, dialog, fs, global-shortcut; adds `tauri_plugin_log` in debug builds; calls `prerequisites::check_ffmpeg` in setup; registers 19 commands in `generate_handler!`.
- src-tauri/src/commands/mod.rs: declares `recording` and `window`.
- src-tauri/src/commands/recording.rs: `save_recording_chunk`, `finalize_recording`, `get_temp_dir`, `read_file_bytes`, private `validate_session_id` and `temp_recording_dir` (`voiceover-recordings` under the system temp dir).
- src-tauri/src/commands/window.rs: `create_widget_window` (label `widget`, 340 by 80, always on top) and `close_widget_window`.
- src-tauri/src/prerequisites.rs: `check_ffmpeg`, `check_prerequisites`, struct `PrerequisiteStatus`.
- src-tauri/build.rs: calls `tauri_build::build()`.

## Calls
`ffmpeg::resolve_ffmpeg_path` from [Backend Pipeline and ffmpeg](./backend-pipeline-and-ffmpeg.md).

## Related
- [Tauri Commands: Recording and Pipeline](../interfaces/tauri-commands-recording-and-pipeline.md)
- [Security Boundaries](../crosscutting/security-boundaries.md)
