---
id: building-blocks/rust-recording-commands
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Rust Recording Commands
description: Commands that store recording chunks in a temp folder, join them, read files back and clean up.
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
related:
  - runtime/record-screen
  - crosscutting/security-boundaries
  - building-blocks/rust-pipeline
  - interfaces/commands-app-config-recording
---

# Rust Recording Commands

`commands/recording.rs` manages files under `<temp>/voiceover-recordings`.

## Functions

- `get_temp_dir()` returns that folder, creating it.
- `save_recording_chunk(session_id, chunk, chunk_index)` writes `chunk_{index:04}.webm` in a per-session folder after `validate_session_id`.
- `finalize_recording(session_id)` sorts the chunk files, appends their bytes into `<session_id>.webm`, removes the chunk folder, and returns the path.
- `read_file_bytes(path)` canonicalizes the path and allows only the temp dir, the video dir, or `~/VoiceOver`.
- `cleanup_stale_recordings(max_age)` removes old session folders, WebM files and extracted/transformed WAV files; `fs_dir_size` is a helper.
- `validate_session_id` accepts alphanumerics, `-` and `_` only.

## Callers

`save_recording_chunk` and `finalize_recording` are called from src/lib/recorder.svelte.ts; `read_file_bytes` from src/routes/preview/+page.svelte; `cleanup_stale_recordings` from src-tauri/src/lib.rs and src-tauri/src/pipeline.rs.

## Related

- [Flow: Record the Screen](../runtime/record-screen.md)
- [Security Boundaries](../crosscutting/security-boundaries.md)
- [Rust Pipeline and ffmpeg](./rust-pipeline.md)
- [Tauri Commands: App, Config, Recording](../interfaces/commands-app-config-recording.md)
