---
id: interfaces/tauri-commands-tts
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Tauri Commands: Local TTS, Models, Sidecar
description: Command names, inputs, outputs and call sites for sidecar-related commands.
domain: architecture
tags:
  - interface
  - tauri
  - sidecar
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/local_tts.rs
  - resource: src-tauri/src/models.rs
  - resource: src-tauri/src/sidecar.rs
  - resource: src/lib/voicebox.ts
  - resource: src/lib/StatusBar.svelte
  - resource: src/routes/(app)/create-voice/+page.svelte
relations:
  relates_to:
    - interfaces/tauri-commands-app
    - interfaces/sidecar-http-api
    - building-blocks/rust-local-tts-and-sidecar
---
# Tauri Commands: Local TTS, Models, Sidecar

Each command below forwards to the sidecar on its current port.

| Command | Inputs | Output | Called from |
|---|---|---|---|
| `test_local_connection` | none | bool | `src/lib/voicebox.ts` |
| `list_local_voices` | none | `Vec<LocalVoice>` | `voicebox.ts`, `StatusBar.svelte`, home, preview, settings pages |
| `check_model_status` | none | `Vec<ModelInfo>` | `src/lib/voicebox.ts` |
| `extract_youtube_audio` | `url`, `start`, `duration` | JSON value | create-voice page |
| `poll_generation` | `generation_id` | JSON value | `src/lib/voicebox.ts` |
| `get_generation_audio` | `generation_id` | bytes | `src/lib/voicebox.ts` |
| `sidecar_fetch` | `path`, `method`, `body` | response text | `voicebox.ts`, create-voice and settings pages |
| `sidecar_upload` | `path`, `file_bytes`, `file_name`, `file_field`, `fields` | response text | `voicebox.ts`, create-voice page |
| `get_sidecar_status` | none | JSON with `running`, `healthy`, `port` | `StatusBar.svelte` |
| `check_models_downloaded` | none | `Vec<ModelInfo>` | no call under `src/` |
| `download_model` | `model`, `on_event` | unit | `src/lib/voicebox.ts` |
| `get_models_disk_usage` | none | `u64` | no call under `src/` |

`sidecar_fetch` allows paths starting with `/health`, `/profiles`, `/generate`, `/audio/`, `/models`, `/transcribe`, `/voice-convert`, `/extract-youtube`, and methods GET, POST, PUT, DELETE (`src-tauri/src/local_tts.rs`). `sidecar_upload` has no path allowlist.

## Related

- [Tauri Commands: Config, Recording, Library, Drive, Window](tauri-commands-app.md)
- [Sidecar HTTP API](sidecar-http-api.md)
- [Rust Local TTS and Sidecar Manager](../building-blocks/rust-local-tts-and-sidecar.md)
