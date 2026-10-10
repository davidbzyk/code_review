---
id: building-blocks/backend-pipeline
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Backend processing pipeline"
description: "The process_recording command that turns a recording into a final MP4."
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
relations:
  relates_to:
    - runtime/process-recording-desktop
    - interfaces/pipeline-events
---

# Backend processing pipeline

`src-tauri/src/pipeline.rs` orchestrates ffmpeg and ElevenLabs and reports progress over a channel.

## Items

- Enum `PipelineEvent` (`Progress { stage, percent }`, `Complete { output_path }`, `Error { message }`), serialized with `tag = "event"`, `content = "data"`, camelCase.
- `process_recording(app, recording_path, voice_replacement, voice_id, on_event)` (async command).
- `cleanup_temp(path)`: `remove_file`, ignoring errors.
- `chrono_timestamp()`: Unix seconds as a string.

## Behaviour

It reads config with `config::get_config`, creates `output_dir` (falling back to the video or home directory plus `VoiceOver`), and names the result `voiceover-<timestamp>.mp4`. Without voice replacement it calls `ffmpeg::normalize_to_mp4`. With it, it requires a non-empty API key, resolves a voice id (argument, then default voice, then first voice), then runs `ffmpeg::extract_audio`, `elevenlabs::speech_to_speech`, `ffmpeg::replace_audio`.

## Calls

[backend-config](./backend-config.md), [backend-ffmpeg](./backend-ffmpeg.md), [backend-elevenlabs](./backend-elevenlabs.md).

## Related

- [runtime/process-recording-desktop](../runtime/process-recording-desktop.md)
- [interfaces/pipeline-events](../interfaces/pipeline-events.md)
- [building-blocks/page-preview](./page-preview.md)
