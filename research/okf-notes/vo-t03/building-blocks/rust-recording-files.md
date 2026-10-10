---
id: building-blocks/rust-recording-files
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Rust recording file commands"
description: "Chunked recording storage in the system temp folder and guarded file reads."
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
  - crosscutting/input-and-path-validation
  - building-blocks/frontend-recorder
---
# Rust recording file commands

`commands/recording.rs` stores recording chunks sent by the webview and joins them into one WebM file.

## Functions

- `validate_session_id`: non-empty, only alphanumeric, `-` or `_`.
- `temp_recording_dir()`: `<temp>/voiceover-recordings`, created on demand.
- `get_temp_dir` returns that path.
- `save_recording_chunk(session_id, chunk, chunk_index)` writes `chunk_<index:04>.webm` under the session folder.
- `finalize_recording(session_id)` lists `.webm` chunks, sorts them by path, appends their bytes to `<session_id>.webm`, deletes the chunk folder, returns the path. It returns the error "No recording data — stopped too quickly" when no chunks exist.
- `read_file_bytes(path)` canonicalizes the path and allows it only under the temp folder, the video folder, or `<home>/VoiceOver`; otherwise returns "Access denied: path outside allowed directories".

## Callers

`recorder.svelte.ts` calls the first, second and third commands; `preview/+page.svelte` calls `read_file_bytes`.

## Related

- [[runtime/record-screen]]
- [[crosscutting/input-and-path-validation]]
- [[building-blocks/frontend-recorder]]
