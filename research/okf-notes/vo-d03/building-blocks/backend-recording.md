---
id: building-blocks/backend-recording
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Backend recording commands"
description: "Commands that store recording chunks in the temp directory and join them into one file."
domain: architecture
tags:
  - building-block
  - backend
  - recording
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/commands/recording.rs
  - resource: src-tauri/src/commands/mod.rs
relations:
  relates_to:
    - runtime/record-screen
    - interfaces/tauri-commands
---

# Backend recording commands

`src-tauri/src/commands/recording.rs` persists the recorder's output under the system temp directory.

## Functions

- `validate_session_id(session_id)`: accepts only alphanumerics, `-` and `_`; empty is an error.
- `temp_recording_dir()`: `std::env::temp_dir()/voiceover-recordings`, created if missing.
- `get_temp_dir` (command): returns that path as a string.
- `save_recording_chunk(session_id, chunk: Vec<u8>, chunk_index: u32)` (command): writes `<session>/chunk_NNNN.webm` and returns its path.
- `read_file_bytes(path)` (command): `fs::read` of any given path.
- `finalize_recording(session_id)` (command): lists `.webm` chunks in the session directory, sorts by path, concatenates them into `<session_id>.webm`, deletes the chunk directory, returns the path.

`src-tauri/src/commands/mod.rs` declares `pub mod recording;` and `pub mod window;`.

## Called by

`src/lib/recorder.svelte.ts` (`save_recording_chunk`, `finalize_recording`) and `src/routes/preview/+page.svelte` (`read_file_bytes`).

## Related

- [runtime/record-screen](../runtime/record-screen.md)
- [building-blocks/frontend-recorder](./frontend-recorder.md)
- [interfaces/tauri-commands](../interfaces/tauri-commands.md)
