---
id: interfaces/commands-pipeline-models-drive
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Tauri Commands: Pipeline, Models, Drive, ElevenLabs
description: Commands for processing a recording, model management, Google Drive and key testing.
domain: architecture
tags:
  - interface
  - tauri
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/pipeline.rs
  - resource: src-tauri/src/models.rs
  - resource: src-tauri/src/google_drive.rs
  - resource: src-tauri/src/elevenlabs.rs
  - resource: src-tauri/src/sidecar.rs
related:
  - interfaces/commands-app-config-recording
  - interfaces/commands-sidecar-proxy
  - interfaces/tauri-events-and-channels
---

# Tauri Commands: Pipeline, Models, Drive, ElevenLabs

| Command | Inputs | Output | Declared in | Called from |
|---|---|---|---|---|
| `process_recording` | `recording_path`, `voice_replacement`, `voice_id: Option<String>`, `on_event: Channel<PipelineEvent>` | output path `String` | pipeline.rs | src/routes/preview/+page.svelte |
| `test_api_key` | `api_key` | `bool` | elevenlabs.rs | src/routes/settings/+page.svelte |
| `check_models_downloaded` | none | `Vec<ModelInfo>` | models.rs | no caller in src/ |
| `download_model` | `model`, `on_event: Channel<ModelDownloadEvent>` | unit | models.rs | no caller in src/ |
| `get_models_disk_usage` | none | `u64` | models.rs | no caller in src/ |
| `google_drive_connect` | `client_id`, `client_secret` | `DriveTokens` | google_drive.rs | src/routes/settings/+page.svelte |
| `google_drive_disconnect` | none | unit | google_drive.rs | no caller in src/ |
| `upload_to_drive` | `access_token`, `file_path`, `on_event: Channel<DriveEvent>` | link `String` | google_drive.rs | src/routes/preview/+page.svelte |
| `get_sidecar_status` | none | JSON `running`, `healthy`, `port` | sidecar.rs | no caller in src/ |

Parameter names are camelCase on the JavaScript side (`recordingPath`, `voiceId`, `onEvent`).

## Related

- [Tauri Commands: App, Config, Recording](./commands-app-config-recording.md)
- [Tauri Commands: Local TTS and Sidecar Proxy](./commands-sidecar-proxy.md)
- [Channels and Window Events](./tauri-events-and-channels.md)
