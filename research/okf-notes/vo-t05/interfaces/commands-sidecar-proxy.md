---
id: interfaces/commands-sidecar-proxy
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Tauri Commands: Local TTS and Sidecar Proxy
description: Commands in local_tts.rs that reach the Python sidecar.
domain: architecture
tags:
  - interface
  - tauri
  - local-tts
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/local_tts.rs
  - resource: src/lib/voicebox.ts
  - resource: src/routes/create-voice/+page.svelte
  - resource: src/routes/settings/+page.svelte
  - resource: src/routes/+page.svelte
related:
  - interfaces/commands-app-config-recording
  - interfaces/sidecar-http-generation
  - interfaces/sidecar-http-profiles-models
  - building-blocks/rust-tts-providers
---

# Tauri Commands: Local TTS and Sidecar Proxy

| Command | Inputs | Output | Sidecar route | Called from |
|---|---|---|---|---|
| `test_local_connection` | none | `bool` | health check on stored port | src/lib/voicebox.ts |
| `list_local_voices` | none | `Vec<LocalVoice>` | GET `/profiles` | voicebox.ts, `/`, `/settings` |
| `check_model_status` | none | `Vec<ModelInfo>` | GET `/models/status` | src/lib/voicebox.ts |
| `extract_youtube_audio` | `url`, `start: String`, `duration: u32` | JSON | POST `/extract-youtube` | create-voice |
| `poll_generation` | `generation_id` | JSON | GET `/generate/{id}/status` | src/lib/voicebox.ts |
| `get_generation_audio` | `generation_id` | `Vec<u8>` | GET `/audio/{id}` | src/lib/voicebox.ts |
| `sidecar_fetch` | `path`, `method`, `body: Option<String>` | response text | any allowed path | voicebox.ts, settings, create-voice |
| `sidecar_upload` | `path`, `file_bytes`, `file_name`, `file_field`, `fields` | response text | multipart POST | voicebox.ts, create-voice |

- `sidecar_fetch` supports methods POST, PUT, DELETE, GET; timeout 120 s. `sidecar_upload` timeout 60 s.
- Allowed prefixes: `/health`, `/profiles`, `/generate`, `/audio/`, `/models`, `/transcribe`, `/voice-convert`, `/extract-youtube`.
- `list_local_voices` and others call `sidecar::ensure_running` first; `poll_generation` and `get_generation_audio` use `get_port` and fail if the sidecar is not running.

## Related

- [Tauri Commands: App, Config, Recording](./commands-app-config-recording.md)
- [Sidecar HTTP: Transcribe, Generate, Audio, Convert, YouTube](./sidecar-http-generation.md)
- [Sidecar HTTP: Profiles and Models](./sidecar-http-profiles-models.md)
- [Rust TTS Providers and Models](../building-blocks/rust-tts-providers.md)
