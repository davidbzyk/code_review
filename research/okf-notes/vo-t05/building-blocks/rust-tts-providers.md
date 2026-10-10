---
id: building-blocks/rust-tts-providers
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Rust TTS Providers and Models
description: ElevenLabs client, local sidecar client, provider enum and model download commands.
domain: architecture
tags:
  - building-block
  - rust
  - tts
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/elevenlabs.rs
  - resource: src-tauri/src/local_tts.rs
  - resource: src-tauri/src/tts_provider.rs
  - resource: src-tauri/src/models.rs
related:
  - interfaces/external-http-apis
  - interfaces/commands-sidecar-proxy
  - building-blocks/rust-sidecar-manager
  - runtime/process-recording-local
  - runtime/process-recording-elevenlabs
---

# Rust TTS Providers and Models

Four modules call the two voice back ends and manage local model files.

## elevenlabs.rs

- `speech_to_speech(api_key, voice_id, input_audio, output_audio)` posts multipart to `S2S_BASE_URL/{voice_id}?output_format=mp3_44100_128` with model `eleven_multilingual_sts_v2`.
- `test_api_key(api_key)` GETs `https://api.elevenlabs.io/v1/user`.

## local_tts.rs

- `speech_to_speech(client, port, profile_id, input_wav, output_wav, video_duration)`: POST `/transcribe`, write a `.txt` transcript, POST `/generate`, then `poll_and_download`.
- `voice_convert(...)`: POST `/voice-convert`, then `poll_and_download`.
- `poll_and_download` polls `/generate/{id}/status` every `POLL_INTERVAL_MS` (500) until `POLL_TIMEOUT_SECS` (300), then GETs `/audio/{id}`.
- Commands: `test_local_connection`, `list_local_voices`, `check_model_status`, `extract_youtube_audio`, `poll_generation`, `get_generation_audio`, `sidecar_fetch`, `sidecar_upload`.
- `ALLOWED_SIDECAR_PATHS` lists the prefixes `sidecar_fetch` accepts.
- `HttpClient` wraps a shared `reqwest::Client`.

## tts_provider.rs and models.rs

- `Provider` enum: `ElevenLabs` (default) and `Local`, serialized `elevenlabs` and `local`.
- `check_models_downloaded`, `download_model` (reads SSE `data:` lines, sends `ModelDownloadEvent`), `get_models_disk_usage`.

## Related

- [External HTTP APIs](../interfaces/external-http-apis.md)
- [Tauri Commands: Local TTS and Sidecar Proxy](../interfaces/commands-sidecar-proxy.md)
- [Rust Sidecar Manager](./rust-sidecar-manager.md)
- [Flow: Process a Recording (Local TTS)](../runtime/process-recording-local.md)
- [Flow: Process a Recording (ElevenLabs)](../runtime/process-recording-elevenlabs.md)
