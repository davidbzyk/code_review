---
id: building-blocks/tauri-recording
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Rust recording commands
description: Rust commands store recording chunks in a temp folder, join them, serve file bytes and manage the widget window.
domain: architecture
tags:
  - building-block
  - rust
  - recording
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/commands/recording.rs
  - resource: src-tauri/src/commands/window.rs
related:
  - runtime/record-screen
  - building-blocks/frontend-recorder
  - interfaces/tauri-commands
---

# Rust recording commands

`commands/recording.rs` handles recorded files under `<temp>/voiceover-recordings`; `commands/window.rs` handles the widget window.

## recording.rs

- `validate_session_id` accepts only alphanumerics, `-` and `_`.
- `get_temp_dir()` returns the recordings folder.
- `save_recording_chunk(session_id, chunk, chunk_index)` writes `chunk_NNNN.webm` under the session folder.
- `finalize_recording(session_id)` sorts the chunk files, appends their bytes to `<session_id>.webm`, removes the chunk folder, and errors with "No recording data" if none exist.
- `read_file_bytes(path)` canonicalizes the path and allows only the temp dir, the video dir, or `~/VoiceOver`.
- `cleanup_stale_recordings(max_age)` deletes entries older than `max_age` and logs the freed megabytes.

## window.rs

- `create_widget_window` opens window label `widget` at `/widget`, 340x80, undecorated, always on top, centered, unless it exists.
- `close_widget_window` closes it.

## Used by

- The frontend recorder ([[building-blocks/frontend-recorder]]); `pipeline.rs` and `lib.rs` call `cleanup_stale_recordings`.

## Related

- [[runtime/record-screen]] - Record a screen session
- [[building-blocks/frontend-recorder]] - Frontend recorder and overlays
- [[interfaces/tauri-commands]] - Tauri commands
