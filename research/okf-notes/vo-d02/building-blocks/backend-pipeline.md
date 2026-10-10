---
id: building-blocks/backend-pipeline
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Rust processing pipeline
description: process_recording and the ffmpeg helpers that turn a recording into a final MP4.
domain: architecture
tags:
  - building-block
  - backend
  - pipeline
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/pipeline.rs
  - resource: src-tauri/src/ffmpeg.rs
related:
  - runtime/process-recording-desktop
  - building-blocks/backend-elevenlabs
  - building-blocks/backend-config
  - interfaces/pipeline-event
---

src-tauri/src/pipeline.rs drives the stages; src-tauri/src/ffmpeg.rs runs the `ffmpeg` program with `tokio::process::Command`.

## pipeline.rs
- `PipelineEvent` enum: `Progress { stage, percent }`, `Complete { output_path }`, `Error { message }`.
- `process_recording(app, recording_path, voice_replacement, on_event)` (command).
- `cleanup_temp`, `chrono_timestamp` (Unix seconds).

## ffmpeg.rs
- `extract_audio`: `-vn -acodec pcm_s16le -ar 16000 -ac 1` to WAV.
- `replace_audio`: maps `0:v` and `1:a`, `-c:v copy -c:a aac -shortest`.
- `normalize_to_mp4`: `-c:v libx264 -preset fast -c:a aac`.
Each returns `Err` with the ffmpeg stderr text on failure.

## Uses
[[building-blocks/backend-config]] (`get_config`), [[building-blocks/backend-elevenlabs]] (`speech_to_speech`).

## Related
[[runtime/process-recording-desktop]], [[interfaces/pipeline-event]]
