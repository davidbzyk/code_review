---
id: interfaces/sidecar-http-routes
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Sidecar HTTP routes"
description: "Routes served by the FastAPI sidecar and the code that calls them."
domain: architecture
tags:
  - interface
  - http
  - sidecar
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/sidecar/server.py
  - resource: src-tauri/src/local_tts.rs
  - resource: src-tauri/src/models.rs
  - resource: src-tauri/src/sidecar.rs
  - resource: src/lib/voicebox.ts
related:
  - building-blocks/sidecar-server
  - interfaces/sidecar-cli-arguments
  - building-blocks/rust-sidecar-client
---
# Sidecar HTTP routes

Defined in src-tauri/sidecar/server.py, served on `127.0.0.1` at the port given by `--port`.

| Route | Inputs | Output | Called by |
|---|---|---|---|
| GET /health | none | `status`, `models.whisper`, `models.qwen` | sidecar.rs `health_check` |
| POST /transcribe | multipart `file` | `text`, `duration` | local_tts.rs `speech_to_speech`, `sidecar_upload` |
| POST /transcribe-path | JSON `audio_path` | `text`, `duration` | `sidecar_fetch` from the create-voice page |
| POST /generate | JSON `profile_id`, `text`, `language` | `id` | local_tts.rs |
| GET /generate/{gen_id}/status | none | `status`, `error` | local_tts.rs, voicebox.ts |
| GET /audio/{gen_id} | none | WAV bytes | local_tts.rs; the page reads it by URL |
| POST /extract-youtube | JSON `url`, `start`, `duration` | `audio_path`, `duration`, `id` | local_tts.rs `extract_youtube_audio` |
| GET /profiles | none | profile list | `list_local_voices` |
| POST /profiles | JSON `name`, `language` | profile | `sidecar_fetch` |
| POST /profiles/{id}/samples | multipart `audio`, form `reference_text` | `id`, `profile_id` | `sidecar_upload` |
| POST /profiles/{id}/samples/from-path | JSON `audio_path`, `reference_text` | `id`, `profile_id` | `sidecar_fetch` |
| DELETE /profiles/{id} | none | `ok` | settings page via `sidecar_fetch` |
| GET /models/status | none | `models` list | `check_model_status`, `check_models_downloaded` |
| POST /models/download | JSON `model` or `model_name` | server-sent events with `progress`, `status` | models.rs `download_model`, `VoiceboxClient.downloadModel` |

Error replies are JSON `{"error": ...}` with status 400, 404 or 500.

## Related

- [[building-blocks/sidecar-server]]
- [[interfaces/sidecar-cli-arguments]]
- [[building-blocks/rust-sidecar-client]]
