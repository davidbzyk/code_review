---
id: interfaces/sidecar-http-api
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Sidecar HTTP API
description: Routes declared by the FastAPI sidecar.
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
relations:
  relates_to:
    - interfaces/tauri-commands-tts
    - building-blocks/sidecar-server
    - runtime/local-voice-conversion
---
# Sidecar HTTP API

The sidecar binds to `--host` (default 127.0.0.1) and the port Rust passes in.

| Route | Input | Output | Caller |
|---|---|---|---|
| GET `/health` | none | `status` and model flags | `health_check` in `sidecar.rs` |
| POST `/transcribe` | multipart `file` | text, duration, segments | `speech_to_speech` |
| POST `/transcribe-path` | `audio_path` | transcription | create-voice page via `sidecar_fetch` |
| POST `/generate` | `profile_id`, `text`, `language`, `segments`, `original_duration` | `{id}` | `speech_to_speech` |
| GET `/generate/{gen_id}/status` | none | `status`, `error` | `poll_and_download`, `poll_generation` |
| GET `/audio/{gen_id}` | none | `audio/wav` bytes | `poll_and_download`, `get_generation_audio` |
| POST `/voice-convert` | `profile_id`, `source_audio_path`, `original_duration` | `{id}` | `voice_convert` |
| POST `/extract-youtube` | `url`, `start`, `duration` | `audio_path`, `duration`, `id` | `extract_youtube_audio` |
| GET, POST `/profiles` | `name`, `language` for POST | profile list or profile | `list_local_voices`, `sidecar_fetch` |
| POST `/profiles/{id}/samples` | multipart `audio`, `reference_text` | sample | `sidecar_upload` |
| POST `/profiles/{id}/samples/from-path` | `audio_path`, `reference_text` | sample | `sidecar_fetch` |
| DELETE `/profiles/{profile_id}` | none | `{ok: true}` | settings page |
| GET `/models/status` | none | `models` list | `check_model_status` |
| POST `/models/download` | `model` or `model_name` | server-sent events with `progress` | `download_model` |

Known model keys map to Hugging Face repos in `model_map` (`src-tauri/sidecar/server.py`).

## Related

- [Tauri Commands: Local TTS, Models, Sidecar](tauri-commands-tts.md)
- [Sidecar Server](../building-blocks/sidecar-server.md)
- [Flow: Local Voice Replacement](../runtime/local-voice-conversion.md)
