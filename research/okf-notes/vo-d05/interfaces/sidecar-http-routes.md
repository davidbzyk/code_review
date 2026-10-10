---
id: interfaces/sidecar-http-routes
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Sidecar HTTP routes
description: Routes served by the FastAPI sidecar on 127.0.0.1 with their inputs and outputs.
domain: architecture
tags:
  - interface
  - http
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/sidecar/server.py
  - resource: src-tauri/src/local_tts.rs
  - resource: src-tauri/src/models.rs
  - resource: src-tauri/src/sidecar.rs
related:
  - interfaces/tauri-commands
  - building-blocks/sidecar-server
  - building-blocks/tauri-local-tts-bridge
---

# Sidecar HTTP routes

All routes are declared in src-tauri/sidecar/server.py; the Rust callers are named in the last column.

| Route | Input | Output | Caller |
|---|---|---|---|
| GET `/health` | none | `{status: "healthy", models}` | sidecar.rs `health_check` |
| POST `/transcribe` | multipart `file` | text, duration, segments | local_tts.rs |
| POST `/transcribe-path` | `audio_path` | same | create-voice via `sidecar_fetch` |
| POST `/generate` | `profile_id, text, language, segments, original_duration` | `{id}` | local_tts.rs, voicebox.ts |
| GET `/generate/{gen_id}/status` | none | `{status, error}` | local_tts.rs `poll_and_download` |
| GET `/audio/{gen_id}` | none | `audio/wav` bytes | local_tts.rs |
| POST `/voice-convert` | `profile_id, source_audio_path` | `{id}` | local_tts.rs `voice_convert` |
| POST `/extract-youtube` | `url, start, duration` | `audio_path, duration, id` | `extract_youtube_audio` |
| GET `/profiles` | none | profile list | `list_local_voices` |
| POST `/profiles` | `name, language` | profile | voicebox.ts |
| POST `/profiles/{id}/samples` | multipart `audio`, `reference_text` | `{id, profile_id}` | `sidecar_upload` |
| POST `/profiles/{id}/samples/from-path` | `audio_path, reference_text` | same | create-voice |
| DELETE `/profiles/{id}` | none | `{ok: true}` | settings `removeLocalVoice` via `sidecar_fetch` |
| GET `/models/status` | none | `{models: [...]}` | models.rs, local_tts.rs |
| POST `/models/download` | `model` or `model_name` | SSE stream | models.rs `download_model` |

`sidecar_fetch` forwards only paths that start with `/health`, `/profiles`, `/generate`, `/audio/`, `/models`, `/transcribe`, `/voice-convert`, `/extract-youtube` (src-tauri/src/local_tts.rs).

## Related

- [[interfaces/tauri-commands]] - Tauri commands
- [[building-blocks/sidecar-server]] - Sidecar server
- [[building-blocks/tauri-local-tts-bridge]] - Rust local TTS bridge
