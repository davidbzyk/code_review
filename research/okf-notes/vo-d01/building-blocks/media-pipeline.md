---
id: building-blocks/media-pipeline
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Media Pipeline"
description: "Backend orchestration of ffmpeg and ElevenLabs steps that turn a recording into the final MP4."
domain: architecture
tags:
  - building-block
  - rust
  - pipeline
  - ffmpeg
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/pipeline.rs
  - resource: src-tauri/src/ffmpeg.rs
  - resource: src-tauri/src/prerequisites.rs
---
# Media Pipeline

`pipeline.rs` runs the processing steps; `ffmpeg.rs` wraps the `ffmpeg` program; `prerequisites.rs` checks that it exists.

## Facts
- `process_recording(app, recording_path, voice_replacement, on_event: Channel<PipelineEvent>)` is the command (src-tauri/src/pipeline.rs).
- `PipelineEvent` has variants `Progress { stage, percent }`, `Complete { output_path }`, `Error { message }`.
- Output name is `voiceover-{unix seconds}.mp4` in `config.output_dir` (`chrono_timestamp`).
- `ffmpeg::extract_audio` makes 16 kHz mono `pcm_s16le` WAV; `replace_audio` maps `0:v` and `1:a` with `-c:v copy -c:a aac -shortest`; `normalize_to_mp4` uses `libx264 -preset fast` and `aac` (src-tauri/src/ffmpeg.rs).
- `check_ffmpeg` runs `ffmpeg -version`; `check_prerequisites` returns `PrerequisiteStatus { ffmpeg_available, ffmpeg_version }` (src-tauri/src/prerequisites.rs).
- `cleanup_temp` deletes the recording and intermediate files.

## Calls
`config::get_config`, `elevenlabs::speech_to_speech`, the `ffmpeg` functions.

## Related
- [[runtime/process-recording-desktop]]
- [[building-blocks/elevenlabs-client]]
- [[building-blocks/config-store]]
- [[interfaces/pipeline-channel-events]]
