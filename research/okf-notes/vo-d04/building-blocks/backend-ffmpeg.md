---
id: building-blocks/backend-ffmpeg
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Backend ffmpeg wrappers and prerequisites"
description: "Functions that run the system ffmpeg program and check that it exists."
domain: architecture
tags:
  - backend
  - ffmpeg
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
architecture_layer: building-blocks
sources:
  - resource: src-tauri/src/ffmpeg.rs
  - resource: src-tauri/src/prerequisites.rs
related:
  - building-blocks/backend-pipeline
  - building-blocks/frontend-shell
  - deployment/build-and-package
---

# Backend ffmpeg wrappers and prerequisites

Two modules start the `ffmpeg` program: `ffmpeg.rs` for media work and `prerequisites.rs` for the availability check.

## Facts
- `extract_audio(input_video, output_wav)`: `-vn -acodec pcm_s16le -ar 16000 -ac 1` (src-tauri/src/ffmpeg.rs).
- `replace_audio(input_video, new_audio, output_mp4)`: maps video of input 0 and audio of input 1, `libx264` preset `fast`, `aac`, `-shortest` (src-tauri/src/ffmpeg.rs).
- `normalize_to_mp4(input, output_mp4)`: `libx264` preset `fast`, `aac` (src-tauri/src/ffmpeg.rs).
- All three use `tokio::process::Command` and return the ffmpeg stderr text in the error string on failure.
- `check_ffmpeg()` runs `ffmpeg -version` (src-tauri/src/prerequisites.rs).
- `check_prerequisites` (command) returns `PrerequisiteStatus { ffmpeg_available, ffmpeg_version }` (src-tauri/src/prerequisites.rs).

## Used by
src-tauri/src/pipeline.rs, src-tauri/src/lib.rs, src/routes/+layout.svelte.

## Related

- [[building-blocks/backend-pipeline]]
- [[building-blocks/frontend-shell]]
- [[deployment/build-and-package]]
