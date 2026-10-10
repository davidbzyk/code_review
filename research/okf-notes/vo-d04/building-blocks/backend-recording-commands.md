---
id: building-blocks/backend-recording-commands
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Backend recording commands"
description: "Commands that store, join and read recording files in the OS temp directory."
domain: architecture
tags:
  - backend
  - commands
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
architecture_layer: building-blocks
sources:
  - resource: src-tauri/src/commands/recording.rs
  - resource: src-tauri/src/commands/mod.rs
related:
  - runtime/record-screen-flow
  - building-blocks/frontend-recorder
  - interfaces/tauri-commands
---

# Backend recording commands

`src-tauri/src/commands/recording.rs` writes recording chunks to disk and joins them.

## Facts (src-tauri/src/commands/recording.rs)
- `temp_recording_dir()`: `std::env::temp_dir()/voiceover-recordings`.
- `validate_session_id`: non-empty, only alphanumerics, `-` and `_`.
- `get_temp_dir()`: returns the temp directory path.
- `save_recording_chunk(session_id, chunk: Vec<u8>, chunk_index: u32)`: writes `chunk_{index:04}.webm` under the session folder; returns the path.
- `finalize_recording(session_id)`: sorts the `.webm` chunks by path, concatenates them into `<session_id>.webm`, removes the chunk folder; returns the path.
- `read_file_bytes(path)`: returns the file as `Vec<u8>`.

## Called from
src/lib/recorder.svelte.ts (`save_recording_chunk`, `finalize_recording`) and src/routes/preview/+page.svelte (`read_file_bytes`).

## Related

- [[runtime/record-screen-flow]]
- [[building-blocks/frontend-recorder]]
- [[interfaces/tauri-commands]]
