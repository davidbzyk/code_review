---
id: building-blocks/backend-ffmpeg
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Backend ffmpeg wrapper"
description: "Async functions that run the ffmpeg program, and the startup availability check."
domain: architecture
tags:
  - building-block
  - backend
  - ffmpeg
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/ffmpeg.rs
  - resource: src-tauri/src/prerequisites.rs
relations:
  relates_to:
    - building-blocks/backend-pipeline
---

# Backend ffmpeg wrapper

`ffmpeg.rs` runs `ffmpeg` through `tokio::process::Command`; `prerequisites.rs` checks that it exists.

## `src-tauri/src/ffmpeg.rs`

- `extract_audio(input_video, output_wav)`: `-vn -acodec pcm_s16le -ar 16000 -ac 1`.
- `replace_audio(input_video, new_audio, output_mp4)`: maps video `0:v` and audio `1:a`, `-c:v libx264 -preset fast -c:a aac -shortest`.
- `normalize_to_mp4(input, output_mp4)`: `-c:v libx264 -preset fast -c:a aac`.
- Each passes `-y`, and on a non-zero exit returns an error string containing stderr.

## `src-tauri/src/prerequisites.rs`

- `check_ffmpeg() -> bool`: runs `ffmpeg -version`.
- `check_prerequisites` (command): returns `PrerequisiteStatus { ffmpeg_available, ffmpeg_version }`; the version is the first line of stdout.

## Used by

`ffmpeg.rs` functions are called from `pipeline.rs`; `check_ffmpeg` from `lib.rs` setup; `check_prerequisites` from `src/routes/+layout.svelte`.

## Related

- [building-blocks/backend-pipeline](./backend-pipeline.md)
- [building-blocks/frontend-shell](./frontend-shell.md)
- [interfaces/tauri-commands](../interfaces/tauri-commands.md)
