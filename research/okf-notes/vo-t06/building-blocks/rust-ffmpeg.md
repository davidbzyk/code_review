---
id: building-blocks/rust-ffmpeg
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Rust ffmpeg and Prerequisites"
description: "Resolution of the ffmpeg binary and the three ffmpeg invocations the pipeline uses."
domain: architecture
tags:
  - building-blocks
  - rust
  - ffmpeg
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/ffmpeg.rs
  - resource: src-tauri/src/prerequisites.rs
relations:
  relates_to:
    - building-blocks/rust-pipeline
    - deployment/build-and-package
---

The ffmpeg module wraps the bundled or system ffmpeg executable; the prerequisites module reports whether it runs.

## Facts

- `resolve_ffmpeg_path()` returns a file named `ffmpeg` next to the current executable when it exists, otherwise the bare name `ffmpeg` for the system PATH (`src-tauri/src/ffmpeg.rs`).
- `extract_audio_args`: `-vn -acodec pcm_s16le -ar 16000 -ac 1` (16 kHz mono WAV).
- `replace_audio_args`: maps video from input 0 and audio from input 1, pads to even dimensions, encodes `libx264` preset `fast` and `aac`, with `-shortest`.
- `normalize_args`: pads to even dimensions, `libx264` preset `fast`, `aac`.
- `extract_audio`, `replace_audio`, `normalize_to_mp4` run `tokio::process::Command` and return `Err` containing stderr text when ffmpeg exits non-zero.
- `check_ffmpeg()` runs `ffmpeg -version` and returns whether it succeeded (`src-tauri/src/prerequisites.rs`).
- The command `check_prerequisites` returns `PrerequisiteStatus { ffmpeg_available, ffmpeg_version }`, where the version is the first line of the `-version` output.
- Callers: `src-tauri/src/pipeline.rs` (ffmpeg functions), `src-tauri/src/lib.rs` (`check_ffmpeg`), `src/routes/+layout.svelte` (`check_prerequisites`).

## Related

- [Rust pipeline](rust-pipeline.md)
- [Build and package](../deployment/build-and-package.md)
