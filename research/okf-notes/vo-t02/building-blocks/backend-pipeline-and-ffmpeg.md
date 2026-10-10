---
id: building-blocks/backend-pipeline-and-ffmpeg
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Backend Pipeline and ffmpeg"
description: "The processing pipeline command and the ffmpeg wrapper."
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
  - building-blocks/backend-tts-providers
  - interfaces/events-and-channels
---
# Backend Pipeline and ffmpeg

This block turns a recorded WebM into a final MP4, with or without voice replacement.

## src-tauri/src/pipeline.rs
Enum `PipelineEvent` (`Progress`, `Complete`, `Error`), command `process_recording`, private `cleanup_temp` and `chrono_timestamp`.

## src-tauri/src/ffmpeg.rs
- `resolve_ffmpeg_path`: a file named `ffmpeg` next to the executable, else `ffmpeg` on PATH.
- Argument builders `extract_audio_args`, `replace_audio_args`, `normalize_args`.
- Async runners `extract_audio`, `replace_audio`, `normalize_to_mp4`.

## Calls
- `config::get_config`, `elevenlabs::speech_to_speech`, `local_tts::speech_to_speech`.

## Related
- [Process Recording on Desktop](../runtime/process-recording-desktop.md)
- [Backend TTS Providers](./backend-tts-providers.md)
- [Events and Channels](../interfaces/events-and-channels.md)
