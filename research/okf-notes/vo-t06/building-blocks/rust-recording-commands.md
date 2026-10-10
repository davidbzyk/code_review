---
id: building-blocks/rust-recording-commands
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Rust Recording Commands"
description: "Commands that store recording chunks on disk, join them and read files back for preview."
domain: architecture
tags:
  - building-blocks
  - rust
  - recording
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/commands/recording.rs
relations:
  relates_to:
    - runtime/record-screen
    - building-blocks/frontend-recorder
    - building-blocks/rust-app-shell
---

The recording module persists MediaRecorder chunks to the system temp directory and joins them into one WebM file.

## Facts

- `temp_recording_dir()` returns `<system temp>/voiceover-recordings` and creates it (`src-tauri/src/commands/recording.rs`).
- `validate_session_id` accepts only alphanumeric characters, `-` and `_`, and rejects an empty string (`src-tauri/src/commands/recording.rs`).
- `save_recording_chunk(session_id, chunk, chunk_index)` writes `chunk_{index:04}.webm` under `<temp>/<session_id>/` and returns the path.
- `finalize_recording(session_id)` lists the `.webm` files in the session folder, sorts them by path, appends their bytes in order to `<temp>/<session_id>.webm`, removes the chunk folder, and returns the output path. It returns the error "No recording data - stopped too quickly" when the folder is missing or holds no chunks.
- `read_file_bytes(path)` canonicalizes the path and returns the file bytes only when the path starts with the temp directory, the video directory, or `~/VoiceOver`; otherwise it returns "Access denied: path outside allowed directories".
- `get_temp_dir()` returns the temp recording directory as a string.
- A `#[cfg(test)]` module in the same file tests session id validation and a save-then-finalize round trip.

## Related

- [Record screen flow](../runtime/record-screen.md)
- [Frontend recorder](frontend-recorder.md)
- [Rust app shell](rust-app-shell.md)
