---
id: building-blocks/rust-pipeline
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Rust Pipeline and ffmpeg
description: The process_recording command, the ffmpeg wrapper and the ElevenLabs client.
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
  - resource: src-tauri/src/elevenlabs.rs
relations:
  relates_to:
    - runtime/record-and-process-recording
    - runtime/local-voice-conversion
    - building-blocks/rust-local-tts-and-sidecar
    - interfaces/events-and-channels
---
# Rust Pipeline and ffmpeg

This group turns a recorded WebM into a final MP4, with or without voice replacement.

## Files

- `pipeline.rs`: command `process_recording` and the event enum `PipelineEvent` (`Progress`, `Complete`, `Error`); helpers `write_meta`, `cleanup_temp`, `chrono_timestamp`.
- `ffmpeg.rs`: `resolve_ffmpeg_path` (bundled `ffmpeg` next to the executable, else `ffmpeg` on PATH), `extract_audio` (16 kHz mono PCM WAV), `replace_audio`, `normalize_to_mp4`, `probe_duration`, `extract_thumbnail`, and argument builders such as `extract_audio_args`.
- `elevenlabs.rs`: `speech_to_speech` posts multipart audio to the speech-to-speech URL built by `s2s_url`; command `test_api_key` calls the `/v1/user` endpoint.

## Calls

`process_recording` calls `config::get_config`, `ffmpeg`, `elevenlabs::speech_to_speech` or `local_tts::speech_to_speech` and `local_tts::voice_convert`, and `sidecar::ensure_running`.

## Constants

`S2S_MODEL_ID` is `eleven_multilingual_sts_v2`; `S2S_OUTPUT_FORMAT` is `mp3_44100_128` (`src-tauri/src/elevenlabs.rs`).

## Related

- [Flow: Record and Process a Recording](../runtime/record-and-process-recording.md)
- [Flow: Local Voice Replacement](../runtime/local-voice-conversion.md)
- [Rust Local TTS and Sidecar Manager](rust-local-tts-and-sidecar.md)
- [Events and Channels](../interfaces/events-and-channels.md)
