---
id: building-blocks/recording-commands
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Recording Commands"
description: "Backend commands that write recording chunks to a temp folder and join them."
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
---
# Recording Commands

`recording.rs` stores incoming WebM chunks on disk and concatenates them when recording stops.

## Facts
- `temp_recording_dir` is `std::env::temp_dir()/voiceover-recordings`, created if missing.
- `get_temp_dir` returns that path as a string.
- `save_recording_chunk(session_id, chunk: Vec<u8>, chunk_index: u32)` writes `chunk_{:04}.webm` in a folder named by the session and returns the file path.
- `finalize_recording(session_id)` lists `.webm` files in the session folder, sorts by path, appends them into `{session_id}.webm`, removes the chunk folder and returns the output path.

## Called by
`ondataavailable` and `stopRecording` in src/lib/recorder.svelte.ts.

## Related
- [[runtime/record-screen-and-voice]]
- [[building-blocks/frontend-recorder]]
- [[interfaces/tauri-commands]]
