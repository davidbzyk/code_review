---
id: building-blocks/rust-pipeline
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Rust Pipeline and ffmpeg
description: The process_recording command and the ffmpeg wrappers it drives.
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
related:
  - runtime/process-recording-elevenlabs
  - runtime/process-recording-local
  - building-blocks/rust-tts-providers
  - building-blocks/rust-sidecar-manager
---

# Rust Pipeline and ffmpeg

`pipeline.rs` runs the conversion from a recording to a final MP4; `ffmpeg.rs` runs ffmpeg and ffprobe.

## pipeline.rs

- `process_recording(app, recording_path, voice_replacement, voice_id, on_event)` returns the output path.
- `PipelineEvent` variants `Progress { stage, percent }`, `Complete { output_path }`, `Error { message }`.
- Output name is `voiceover-{timestamp}.mp4`; if the configured output folder cannot be created it falls back to `<videos or home>/VoiceOver`.
- `cleanup_temp` removes temp files.

## ffmpeg.rs

- `resolve_ffmpeg_path()` prefers an `ffmpeg` file next to the executable, else `ffmpeg` on PATH.
- `extract_audio` (16 kHz mono `pcm_s16le`), `replace_audio` (libx264 preset fast, aac), `normalize_to_mp4`, `probe_duration` (ffprobe first, then a decode of `ffmpeg -f null`).
- `extract_audio_args`, `replace_audio_args`, `normalize_args` build the argument lists; `parse_ffmpeg_time` parses `HH:MM:SS`.
- Video filter `pad=ceil(iw/2)*2:ceil(ih/2)*2` is used in `replace_audio_args` and `normalize_args`.

## Calls

`config`, `elevenlabs`, `local_tts`, `sidecar`, `commands::recording`.

## Related

- [Flow: Process a Recording (ElevenLabs)](../runtime/process-recording-elevenlabs.md)
- [Flow: Process a Recording (Local TTS)](../runtime/process-recording-local.md)
- [Rust TTS Providers and Models](./rust-tts-providers.md)
- [Rust Sidecar Manager](./rust-sidecar-manager.md)
