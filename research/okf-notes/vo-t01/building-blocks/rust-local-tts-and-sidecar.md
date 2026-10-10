---
id: building-blocks/rust-local-tts-and-sidecar
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Rust Local TTS and Sidecar Manager
description: Rust code that starts the Python sidecar and talks to it over HTTP.
domain: architecture
tags:
  - building-block
  - rust
  - sidecar
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/local_tts.rs
  - resource: src-tauri/src/sidecar.rs
  - resource: src-tauri/src/models.rs
relations:
  relates_to:
    - runtime/sidecar-startup
    - runtime/local-voice-conversion
    - interfaces/sidecar-http-api
    - building-blocks/sidecar-server
    - interfaces/tauri-commands-tts
---
# Rust Local TTS and Sidecar Manager

These modules own the sidecar process and every HTTP call to it.

## `sidecar.rs`

`SidecarState` holds the child process, port, data dir, a `starting` flag and a `Notify`. Functions: `start_sidecar`, `health_check`, `stop_sidecar`, `ensure_running`, `get_port`; command `get_sidecar_status`.

## `local_tts.rs`

- `HttpClient` wraps one shared `reqwest::Client`.
- `speech_to_speech` and `voice_convert` call the sidecar; `poll_and_download` polls `/generate/{id}/status` and downloads `/audio/{id}`.
- Commands: `test_local_connection`, `list_local_voices`, `check_model_status`, `extract_youtube_audio`, `poll_generation`, `get_generation_audio`, `sidecar_fetch`, `sidecar_upload`.
- `ALLOWED_SIDECAR_PATHS` limits `sidecar_fetch`.

## `models.rs`

Commands `check_models_downloaded`, `download_model` (reads the sidecar's server-sent events and sends `ModelDownloadEvent`), `get_models_disk_usage`.

## Uses

`ffmpeg::resolve_ffmpeg_path`, the Python server in `src-tauri/sidecar/server.py`.

## Related

- [Flow: Sidecar Startup and Health](../runtime/sidecar-startup.md)
- [Flow: Local Voice Replacement](../runtime/local-voice-conversion.md)
- [Sidecar HTTP API](../interfaces/sidecar-http-api.md)
- [Sidecar Server](sidecar-server.md)
- [Tauri Commands: Local TTS, Models, Sidecar](../interfaces/tauri-commands-tts.md)
