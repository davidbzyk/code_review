---
id: interfaces/sidecar-http-generation
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Sidecar HTTP: Transcribe, Generate, Audio, Convert, YouTube
description: Routes in server.py for speech work.
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
related:
  - interfaces/sidecar-http-profiles-models
  - interfaces/commands-sidecar-proxy
  - building-blocks/sidecar-server
---

# Sidecar HTTP: Transcribe, Generate, Audio, Convert, YouTube

All routes are on `127.0.0.1:<port>`; errors are `{"error": ...}` with a status code.

| Route | Inputs | Output |
|---|---|---|
| GET `/health` | none | `{status: "healthy", models: {whisper, qwen}}` |
| POST `/transcribe` | multipart `file` | `{text, duration, segments}` |
| POST `/transcribe-path` | JSON `audio_path` | same |
| POST `/generate` | JSON `profile_id`, `text`, `language`, `segments`, `original_duration` | `{id}` |
| GET `/generate/{gen_id}/status` | path id | `{status, error}` |
| GET `/audio/{gen_id}` | path id | WAV bytes |
| POST `/voice-convert` | JSON `profile_id`, `source_audio_path`, `original_duration` | `{id}` |
| POST `/extract-youtube` | JSON `url`, `start`, `duration` | `{audio_path, duration, id}` |

- `/generate` and `/voice-convert` return 400 when required fields are missing.
- Status values set in `_do_generate`: `queued`, `loading_model`, `preparing_voice`, `generating`, then `completed` or `error`.
- Declared in src-tauri/sidecar/server.py; called from src-tauri/src/local_tts.rs (`speech_to_speech`, `voice_convert`, `poll_and_download`, `extract_youtube_audio`).

## Related

- [Sidecar HTTP: Profiles and Models](./sidecar-http-profiles-models.md)
- [Tauri Commands: Local TTS and Sidecar Proxy](./commands-sidecar-proxy.md)
- [Sidecar Server](../building-blocks/sidecar-server.md)
