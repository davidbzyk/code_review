---
id: interfaces/tauri-commands
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Tauri commands"
description: "Every command registered in generate_handler, with inputs, outputs and declaring file."
domain: architecture
tags:
  - interface
  - tauri
  - commands
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/lib.rs
  - resource: src-tauri/src/config.rs
  - resource: src-tauri/src/commands/recording.rs
  - resource: src-tauri/src/commands/window.rs
  - resource: src-tauri/src/pipeline.rs
  - resource: src-tauri/src/elevenlabs.rs
  - resource: src-tauri/src/local_tts.rs
  - resource: src-tauri/src/sidecar.rs
  - resource: src-tauri/src/models.rs
  - resource: src-tauri/src/google_drive.rs
  - resource: src-tauri/src/prerequisites.rs
related:
  - interfaces/pipeline-events
  - building-blocks/tauri-host
---
# Tauri commands

`generate_handler!` in src-tauri/src/lib.rs registers 24 commands. All return `Result<_, String>` except `get_temp_dir`, which returns a plain `String`.

| Command | Inputs | Output | Declared in |
|---|---|---|---|
| check_prerequisites | none | `PrerequisiteStatus` | prerequisites.rs |
| get_config / save_config | none / `config` | `AppConfig` / unit | config.rs |
| save_recording_chunk | `session_id`, `chunk`, `chunk_index` | path string | commands/recording.rs |
| finalize_recording | `session_id` | path string | commands/recording.rs |
| get_temp_dir | none | string | commands/recording.rs |
| read_file_bytes | `path` | bytes | commands/recording.rs |
| create_widget_window / close_widget_window | none | unit | commands/window.rs |
| process_recording | `recording_path`, `voice_replacement`, `voice_id`, `on_event` | output path | pipeline.rs |
| test_api_key | `api_key` | bool | elevenlabs.rs |
| test_local_connection | none | bool | local_tts.rs |
| list_local_voices | none | `Vec<LocalVoice>` | local_tts.rs |
| check_model_status | none | `Vec<ModelInfo>` | local_tts.rs |
| extract_youtube_audio | `url`, `start`, `duration` | JSON value | local_tts.rs |
| sidecar_fetch | `path`, `method`, `body` | response text | local_tts.rs |
| sidecar_upload | `path`, `file_bytes`, `file_name`, `file_field`, `fields` | response text | local_tts.rs |
| get_sidecar_status | none | JSON `running`, `healthy`, `port` | sidecar.rs |
| check_models_downloaded | none | `Vec<ModelInfo>` | models.rs |
| download_model | `model`, `on_event` | unit | models.rs |
| get_models_disk_usage | none | `u64` bytes | models.rs |
| google_drive_connect | `client_id`, `client_secret` | `DriveTokens` | google_drive.rs |
| google_drive_disconnect | none | unit | google_drive.rs |
| upload_to_drive | `access_token`, `file_path`, `on_event` | link string | google_drive.rs |

Callers are the Svelte pages and `src/lib/*.ts` through `tauriInvoke` or `invoke`.

## Related

- [[interfaces/pipeline-events]]
- [[building-blocks/tauri-host]]
