---
id: building-blocks/rust-recording-commands
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Rust recording commands"
description: "commands/recording.rs writes recording chunks into a temp folder and joins them into one WebM file."
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
relations:
  relates_to:
    - runtime/record-screen-flow
    - interfaces/tauri-commands
    - building-blocks/frontend-recorder
---
# Rust recording commands

The recording commands store MediaRecorder output on disk during a Tauri session.

## Facts (src-tauri/src/commands/recording.rs)

- `validate_session_id` accepts only alphanumerics, `-` and `_`, and rejects empty ids.
- `temp_recording_dir()` is `<system temp>/voiceover-recordings`, created if missing.
- `get_temp_dir()` returns that path as a string.
- `save_recording_chunk(session_id, chunk: Vec<u8>, chunk_index: u32)` writes `chunk_<index as 4 digits>.webm` under a per-session folder and returns the path.
- `finalize_recording(session_id)` lists `.webm` files in the session folder, sorts them by path, appends their bytes into `<session_id>.webm`, removes the session folder and returns the output path.
- `read_file_bytes(path)` returns the file as `Vec<u8>` (used by the preview page).
- The in-file `tests` module covers id validation and a save/finalize round trip.

## Called by

src/lib/recorder.svelte.ts (`save_recording_chunk`, `finalize_recording`) and src/routes/preview/+page.svelte (`read_file_bytes`).

## Related

[[runtime/record-screen-flow]], [[interfaces/tauri-commands]], [[building-blocks/frontend-recorder]]
