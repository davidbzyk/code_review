---
id: building-blocks/tauri-media-pipeline
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Rust media pipeline
description: process_recording drives audio extraction, voice transformation and re-muxing through ffmpeg.rs, elevenlabs.rs and local_tts.rs.
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
related:
  - runtime/process-recording-elevenlabs
  - runtime/process-recording-local-tts
  - building-blocks/tauri-local-tts-bridge
---

# Rust media pipeline

Three modules turn a finished recording into an MP4 with replaced audio.

## pipeline.rs

- `process_recording(app, recording_path, voice_replacement, voice_id, on_event)` returns the final path; `PipelineEvent` has `Progress { stage, percent }`, `Complete { output_path }`, `Error { message }`.
- Output file name is `voiceover-<unix seconds>.mp4` in `config.output_dir`, with a fallback folder when creation fails.

## ffmpeg.rs

- `resolve_ffmpeg_path()` prefers an `ffmpeg` next to the executable, else `ffmpeg` on PATH.
- `extract_audio` (16 kHz mono `pcm_s16le`), `replace_audio` (libx264 `-preset fast`, aac, even-size pad), `normalize_to_mp4`, `probe_duration` (ffprobe, then an ffmpeg decode fallback).
- Argument builders: `extract_audio_args`, `replace_audio_args`, `normalize_args`.

## elevenlabs.rs

- Constants `S2S_BASE_URL`, `S2S_OUTPUT_FORMAT` (`mp3_44100_128`), `S2S_MODEL_ID` (`eleven_multilingual_sts_v2`), `API_KEY_HEADER` (`xi-api-key`).
- `speech_to_speech(api_key, voice_id, input_audio, output_audio)` and command `test_api_key`.

## Uses

- Local mode uses [[building-blocks/tauri-local-tts-bridge]]; configuration comes from [[building-blocks/tauri-config-secrets]].

## Related

- [[runtime/process-recording-elevenlabs]] - Process recording with ElevenLabs
- [[runtime/process-recording-local-tts]] - Process recording with local TTS
- [[building-blocks/tauri-local-tts-bridge]] - Rust local TTS bridge
