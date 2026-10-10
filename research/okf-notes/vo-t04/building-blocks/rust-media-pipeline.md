---
id: building-blocks/rust-media-pipeline
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Rust media pipeline"
description: "pipeline.rs, ffmpeg.rs and prerequisites.rs turn a recording into the final MP4 using ffmpeg and ElevenLabs."
domain: architecture
tags:
  - building-block
  - rust
  - pipeline
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/pipeline.rs
  - resource: src-tauri/src/ffmpeg.rs
  - resource: src-tauri/src/prerequisites.rs
relations:
  relates_to:
    - building-blocks/rust-elevenlabs
    - runtime/process-recording-tauri
    - interfaces/tauri-commands
---
# Rust media pipeline

The media pipeline coordinates ffmpeg runs and the voice transform for one recording.

## Files

- src-tauri/src/pipeline.rs: command `process_recording(app, recording_path, voice_replacement, voice_id, on_event)`; enum `PipelineEvent` (`Progress`, `Complete`, `Error`, serialised as `{event, data}` in camelCase); helpers `cleanup_temp`, `chrono_timestamp`.
- src-tauri/src/ffmpeg.rs: `resolve_ffmpeg_path()` (a file named `ffmpeg` next to the executable, else `ffmpeg` on PATH); argument builders `extract_audio_args`, `replace_audio_args`, `normalize_args`; async `extract_audio`, `replace_audio`, `normalize_to_mp4`.
- src-tauri/src/prerequisites.rs: `check_ffmpeg()` runs `ffmpeg -version`; command `check_prerequisites` returns `PrerequisiteStatus { ffmpeg_available, ffmpeg_version }`.

## Uses

`config::get_config`, `elevenlabs::speech_to_speech`, `tokio::process::Command`.

## Related

[[building-blocks/rust-elevenlabs]], [[runtime/process-recording-tauri]], [[interfaces/tauri-commands]]
