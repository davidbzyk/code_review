---
id: building-blocks/rust-recording-and-library
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Rust Recording and Library
description: Chunk storage for recordings and the library of finished MP4 files.
domain: architecture
tags:
  - building-block
  - rust
  - files
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/commands/recording.rs
  - resource: src-tauri/src/library.rs
relations:
  relates_to:
    - runtime/record-and-process-recording
    - crosscutting/path-validation
    - building-blocks/rust-pipeline
    - building-blocks/frontend-recorder
---
# Rust Recording and Library

These modules store recorder chunks under the temp directory and manage finished recordings in the output directory.

## `commands/recording.rs`

- `save_recording_chunk(session_id, chunk, chunk_index)` writes `chunk_NNNN.webm` under `voiceover-recordings/<session_id>` in the system temp dir.
- `finalize_recording(session_id)` appends the sorted chunks into `<session_id>.webm` and removes the chunk folder.
- `read_file_bytes(path)` reads a file only under the temp dir, the video dir or `~/VoiceOver`.
- `get_temp_dir`, `cleanup_stale_recordings(max_age)`, `validate_session_id`.

## `library.rs`

- `list_recordings` scans the output directory for `.mp4` files and reads `.meta.json` companions into `RecordingInfo`.
- `generate_thumbnail` caches `.thumbnails/<stem>.jpg`.
- `delete_recording`, `rename_recording`, `open_in_system`, `reveal_in_finder` check the path with `validate_in_output_dir`.
- `resolve_output_dir` falls back to the video dir plus `VoiceOver` when the configured folder is missing.

## Uses

`config::get_config`, `ffmpeg::extract_thumbnail`.

## Related

- [Flow: Record and Process a Recording](../runtime/record-and-process-recording.md)
- [Path and Input Validation](../crosscutting/path-validation.md)
- [Rust Pipeline and ffmpeg](rust-pipeline.md)
- [Frontend Recorder](frontend-recorder.md)
