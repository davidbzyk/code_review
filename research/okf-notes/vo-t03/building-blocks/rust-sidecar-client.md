---
id: building-blocks/rust-sidecar-client
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Rust sidecar client"
description: "Process management for the TTS sidecar and the Rust-side HTTP clients that call it."
domain: architecture
tags:
  - building-block
  - rust
  - sidecar
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/sidecar.rs
  - resource: src-tauri/src/local_tts.rs
  - resource: src-tauri/src/models.rs
related:
  - building-blocks/sidecar-server
  - runtime/sidecar-startup
  - interfaces/sidecar-http-routes
---
# Rust sidecar client

These files start the sidecar, keep it alive and forward requests to it over loopback HTTP.

## sidecar.rs

- `SidecarState` with mutex-guarded `child`, `port`, `data_dir`, `starting`.
- `start_sidecar`, `ensure_running`, `health_check`, `stop_sidecar`, `get_port`; command `get_sidecar_status`.
- `resolve_sidecar_path` (bundled `voiceover-tts`, skipped when `debug_assertions`), `resolve_dev_server_path` (`sidecar/server.py`), `find_available_port`.
- Constants `HEALTH_CHECK_TIMEOUT_SECS = 60`, `HEALTH_CHECK_INTERVAL_MS = 500`.

## local_tts.rs

- `speech_to_speech(port, profile_id, input_wav, output_wav)`: transcribe, generate, poll, download.
- Commands `test_local_connection`, `list_local_voices`, `check_model_status`, `extract_youtube_audio`, `sidecar_fetch`, `sidecar_upload`.
- Types `LocalVoice`, `ModelInfo`, `ModelsResponse`; constants `POLL_INTERVAL_MS = 500`, `POLL_TIMEOUT_SECS = 300`.

## models.rs

- Commands `check_models_downloaded`, `download_model` (reads the sidecar's `data:` lines and forwards `ModelDownloadEvent`), `get_models_disk_usage` (sums file sizes under `<app data>/models`).

## Related

- [[building-blocks/sidecar-server]]
- [[runtime/sidecar-startup]]
- [[interfaces/sidecar-http-routes]]
