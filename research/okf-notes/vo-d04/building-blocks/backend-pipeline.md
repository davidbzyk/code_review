---
id: building-blocks/backend-pipeline
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Backend processing pipeline"
description: "The process_recording command that turns a recording into a final MP4."
domain: architecture
tags:
  - backend
  - pipeline
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
architecture_layer: building-blocks
sources:
  - resource: src-tauri/src/pipeline.rs
related:
  - runtime/process-recording-desktop-flow
  - building-blocks/backend-ffmpeg
  - building-blocks/backend-elevenlabs
  - interfaces/pipeline-events
---

# Backend processing pipeline

`src-tauri/src/pipeline.rs` runs the extract, transform and splice stages and reports progress over a channel.

## Facts (src-tauri/src/pipeline.rs)
- Enum `PipelineEvent`: `Progress { stage, percent }`, `Complete { output_path }`, `Error { message }`, serialized with `tag = "event"`, `content = "data"`, camelCase.
- `process_recording(app, recording_path, voice_replacement, voice_id, on_event: Channel<PipelineEvent>)` returns the output path.
- Output folder: `config.output_dir`, with a fallback to `<video dir or home>/VoiceOver`.
- Output name: `voiceover-<unix seconds>.mp4`.
- Helpers `cleanup_temp` (removes a file) and `chrono_timestamp`.

## Calls
`config::get_config`, `ffmpeg::normalize_to_mp4`, `ffmpeg::extract_audio`, `ffmpeg::replace_audio`, `elevenlabs::speech_to_speech`.

## Related

- [[runtime/process-recording-desktop-flow]]
- [[building-blocks/backend-ffmpeg]]
- [[building-blocks/backend-elevenlabs]]
- [[interfaces/pipeline-events]]
