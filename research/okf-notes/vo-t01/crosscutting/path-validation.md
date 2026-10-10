---
id: crosscutting/path-validation
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Path and Input Validation
description: Checks that limit which files and endpoints each command can reach.
domain: architecture
tags:
  - crosscutting
  - security
  - validation
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/commands/recording.rs
  - resource: src-tauri/src/library.rs
  - resource: src-tauri/src/local_tts.rs
  - resource: src-tauri/sidecar/server.py
  - resource: src-tauri/sidecar/profiles.py
  - resource: src-tauri/src/google_drive.rs
relations:
  relates_to:
    - building-blocks/rust-recording-and-library
    - interfaces/tauri-commands-tts
    - building-blocks/sidecar-server
---
# Path and Input Validation

Several modules check identifiers and paths before use.

## Facts

- `validate_session_id` accepts alphanumerics, `-` and `_` (`src-tauri/src/commands/recording.rs`).
- `read_file_bytes` canonicalizes the path and requires it under the temp dir, the video dir or `~/VoiceOver`.
- `validate_in_output_dir` canonicalizes and requires the file to be under the output dir (`src-tauri/src/library.rs`).
- `rename_recording` rejects empty names and names with `/`, `\` or NUL.
- `validate_generation_id` accepts ASCII alphanumerics and `-` (`src-tauri/src/local_tts.rs`).
- `sidecar_fetch` checks the path against `ALLOWED_SIDECAR_PATHS` and a method list.
- `_validate_path` in the sidecar rejects NUL and paths outside the data dir or temp dir.
- `/extract-youtube` accepts only https URLs on youtube.com, www.youtube.com, m.youtube.com, youtu.be.
- `_validate_profile_id` accepts `[a-zA-Z0-9_-]+` (`src-tauri/sidecar/profiles.py`).
- `upload_to_drive` canonicalizes the path and rejects `..` (`src-tauri/src/google_drive.rs`).

## Related

- [Rust Recording and Library](../building-blocks/rust-recording-and-library.md)
- [Tauri Commands: Local TTS, Models, Sidecar](../interfaces/tauri-commands-tts.md)
- [Sidecar Server](../building-blocks/sidecar-server.md)
