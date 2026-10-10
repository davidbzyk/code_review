---
id: building-blocks/rust-pipeline
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Rust Pipeline"
description: "The process_recording command that turns a recorded WebM into a final MP4."
domain: architecture
tags:
  - building-blocks
  - rust
  - pipeline
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/pipeline.rs
relations:
  relates_to:
    - runtime/process-recording-tauri
    - building-blocks/rust-ffmpeg
    - building-blocks/rust-elevenlabs
---

The pipeline module runs the ffmpeg and ElevenLabs steps and reports progress over a Tauri channel.

## Facts

- `PipelineEvent` has variants `Progress { stage, percent }`, `Complete { output_path }` and `Error { message }`, serialized with `tag = "event"`, `content = "data"` and camelCase names (`src-tauri/src/pipeline.rs`).
- `process_recording(app, recording_path, voice_replacement, voice_id, on_event)` is the command. It returns `Err("Recording file not found")` when the input is missing.
- Output folder: `config.output_dir`; if it cannot be created, the fallback is `<video dir or home>/VoiceOver`.
- Output file name: `voiceover-{unix seconds}.mp4` from `chrono_timestamp()`.
- Without voice replacement: sends `Progress` "Saving" at 50, runs `ffmpeg::normalize_to_mp4`, sends `Complete`.
- With voice replacement: needs a non-empty `elevenlabs_api_key`; picks `voice_id`, else the config voice with `is_default`, else the first voice. Steps: `ffmpeg::extract_audio` (5 then 10 percent), `elevenlabs::speech_to_speech` (15 then 85), `ffmpeg::replace_audio` (90), `Complete`.
- `cleanup_temp` removes the recording and the intermediate `.wav` and `.mp3` files after success.
- Failures are returned as `Err(String)`; the function does not send `Error` events.

## Related

- [Process recording, desktop](../runtime/process-recording-tauri.md)
- [Rust ffmpeg](rust-ffmpeg.md)
- [Rust ElevenLabs](rust-elevenlabs.md)
