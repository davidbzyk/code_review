---
id: building-blocks/rust-pipeline
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Rust processing pipeline"
description: "The process_recording command, the ffmpeg wrapper and the ElevenLabs client."
domain: architecture
tags:
  - building-block
  - rust
  - pipeline
  - ffmpeg
  - elevenlabs
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/pipeline.rs
  - resource: src-tauri/src/ffmpeg.rs
  - resource: src-tauri/src/elevenlabs.rs
related:
  - runtime/process-recording
  - building-blocks/rust-sidecar-client
  - building-blocks/rust-config-and-secrets
  - interfaces/pipeline-events
---
# Rust processing pipeline

These three files turn a finished recording into an MP4, with or without voice replacement.

## pipeline.rs

- `process_recording(app, recording_path, voice_replacement, voice_id, on_event)` runs the stages described in [[runtime/process-recording]].
- Enum `PipelineEvent` (`Progress`, `Complete`, `Error`) is sent over a Tauri `Channel`.
- `cleanup_temp`, `chrono_timestamp` (seconds since the Unix epoch).

## ffmpeg.rs

- `resolve_ffmpeg_path()`: an `ffmpeg` next to the current executable, else `ffmpeg` on PATH.
- Argument builders `extract_audio_args`, `replace_audio_args`, `normalize_args`.
- Async `extract_audio` (16 kHz mono `pcm_s16le`), `replace_audio` (`libx264`, `aac`, `-shortest`), `normalize_to_mp4`.

## elevenlabs.rs

- Constants `S2S_BASE_URL`, `S2S_OUTPUT_FORMAT` (`mp3_44100_128`), `S2S_MODEL_ID` (`eleven_multilingual_sts_v2`), `API_KEY_HEADER` (`xi-api-key`), `USER_ENDPOINT`.
- `s2s_url(voice_id)`, `speech_to_speech(api_key, voice_id, input_audio, output_audio)`, command `test_api_key`.

## Uses

`config::get_config`, `local_tts::speech_to_speech`, `sidecar::ensure_running`.

## Related

- [[building-blocks/rust-sidecar-client]]
- [[building-blocks/rust-config-and-secrets]]
- [[interfaces/pipeline-events]]
