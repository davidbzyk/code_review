---
id: interfaces/sidecar-http-profiles-models
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Sidecar HTTP: Profiles and Models
description: Routes in server.py for voice profiles and model files.
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
  - resource: src-tauri/sidecar/profiles.py
  - resource: src-tauri/src/models.rs
  - resource: src/lib/voicebox.ts
related:
  - interfaces/sidecar-http-generation
  - interfaces/commands-sidecar-proxy
  - building-blocks/sidecar-engine
---

# Sidecar HTTP: Profiles and Models

| Route | Inputs | Output |
|---|---|---|
| GET `/profiles` | none | list of profile dicts |
| POST `/profiles` | JSON `name`, `language` | profile dict (`id`, `name`, `language`, `created_at`) |
| POST `/profiles/{profile_id}/samples` | multipart `audio`, form `reference_text` | `{id, profile_id}` |
| POST `/profiles/{profile_id}/samples/from-path` | JSON `audio_path`, `reference_text` | `{id, profile_id}` |
| DELETE `/profiles/{profile_id}` | path id | `{ok: true}` or 404 |
| GET `/models/status` | none | `{models: [{model_name, display_name, downloaded, loaded}]}` |
| POST `/models/download` | JSON `model_name` or `model` | SSE `data:` lines with `progress` and `status` |

- `/models/download` maps `whisper` and `qwen` names to `mlx-community/whisper-large-v3-turbo` and `Qwen/Qwen3-TTS-12Hz-1.7B-Base`; an unknown name returns 400.
- Declared in src-tauri/sidecar/server.py, which calls profiles.py; called through `sidecar_fetch` and `sidecar_upload` from src/lib/voicebox.ts and from src-tauri/src/models.rs.

## Related

- [Sidecar HTTP: Transcribe, Generate, Audio, Convert, YouTube](./sidecar-http-generation.md)
- [Tauri Commands: Local TTS and Sidecar Proxy](./commands-sidecar-proxy.md)
- [Sidecar Engine Modules](../building-blocks/sidecar-engine.md)
