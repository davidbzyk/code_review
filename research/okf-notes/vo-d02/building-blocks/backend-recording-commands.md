---
id: building-blocks/backend-recording-commands
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Rust recording commands
description: Commands that store recording chunks in a temp folder and join them into one file.
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
related:
  - building-blocks/frontend-recorder
  - runtime/record-a-session
  - crosscutting/error-handling
---

src-tauri/src/commands/recording.rs writes chunks under `<system temp>/voiceover-recordings/<session_id>/`.

## Functions
- `validate_session_id`: non-empty, only alphanumeric, `-` or `_`.
- `temp_recording_dir()`: creates `voiceover-recordings` in `std::env::temp_dir()`.
- `get_temp_dir` (command): returns that path.
- `save_recording_chunk(session_id, chunk, chunk_index)`: writes `chunk_NNNN.webm`, returns its path.
- `finalize_recording(session_id)`: lists `.webm` chunks, sorts by path, concatenates into `<session_id>.webm`, removes the chunk folder, returns the path.

src-tauri/src/commands/mod.rs declares `pub mod recording; pub mod window;`.

## Related
[[building-blocks/frontend-recorder]], [[runtime/record-a-session]], [[crosscutting/error-handling]]
