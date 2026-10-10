---
id: building-blocks/tauri-local-tts-bridge
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Rust local TTS bridge
description: local_tts.rs, models.rs and sidecar.rs start the Python sidecar and forward requests to it over loopback HTTP.
domain: architecture
tags:
  - building-block
  - rust
  - local-tts
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/local_tts.rs
  - resource: src-tauri/src/models.rs
  - resource: src-tauri/src/sidecar.rs
related:
  - runtime/sidecar-startup
  - runtime/process-recording-local-tts
  - building-blocks/sidecar-server
  - interfaces/sidecar-http-routes
---

# Rust local TTS bridge

These modules own the sidecar process and every HTTP call to it.

## sidecar.rs

- `SidecarState` holds the child process, port, data dir and a `starting` flag.
- `start_sidecar`, `ensure_running`, `health_check`, `stop_sidecar`, `get_port`, and command `get_sidecar_status` (returns `running`, `healthy`, `port`).
- Constants `HEALTH_CHECK_TIMEOUT_SECS` (60) and `HEALTH_CHECK_INTERVAL_MS` (500).

## local_tts.rs

- `speech_to_speech(port, profile_id, input_wav, output_wav, video_duration)`: `/transcribe`, write a `.txt` transcript, `/generate`, then `poll_and_download`.
- `voice_convert(...)`: `/voice-convert`, then `poll_and_download`. Polling every 500 ms, timeout 300 s.
- Commands: `test_local_connection`, `list_local_voices`, `check_model_status`, `extract_youtube_audio`, `poll_generation`, `sidecar_fetch`, `sidecar_upload`.
- `sidecar_fetch` only forwards paths starting with an entry of `ALLOWED_SIDECAR_PATHS`.

## models.rs

- `check_models_downloaded`, `download_model` (reads the SSE body and sends `ModelDownloadEvent` on a channel), `get_models_disk_usage` (sums the `models` folder in app data).

## Uses

- Calls the routes in [[interfaces/sidecar-http-routes]] served by [[building-blocks/sidecar-server]].

## Related

- [[runtime/sidecar-startup]] - Sidecar startup
- [[runtime/process-recording-local-tts]] - Process recording with local TTS
- [[building-blocks/sidecar-server]] - Sidecar server
- [[interfaces/sidecar-http-routes]] - Sidecar HTTP routes
