---
id: interfaces/tauri-commands
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Tauri commands
description: Every Rust command registered in generate_handler, with its main parameters and the files that call it.
domain: architecture
tags:
  - interface
  - ipc
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/lib.rs
  - resource: src-tauri/src/commands/recording.rs
  - resource: src-tauri/src/commands/window.rs
  - resource: src-tauri/src/config.rs
  - resource: src-tauri/src/pipeline.rs
  - resource: src-tauri/src/elevenlabs.rs
  - resource: src-tauri/src/local_tts.rs
  - resource: src-tauri/src/models.rs
  - resource: src-tauri/src/google_drive.rs
  - resource: src-tauri/src/prerequisites.rs
related:
  - interfaces/sidecar-http-routes
  - building-blocks/tauri-core
  - building-blocks/frontend-routes
---

# Tauri commands

The commands below are registered in `tauri::generate_handler!` (src-tauri/src/lib.rs); the page calls them through `invoke` or `tauriInvoke`.

| Command | Parameters | Returns | Called from |
|---|---|---|---|
| `check_prerequisites` | none | `PrerequisiteStatus` | src/routes/+layout.svelte |
| `get_config`, `save_config` | `config: AppConfig` for save | `AppConfig` / unit | src/lib/state.svelte.ts |
| `save_recording_chunk` | `session_id, chunk, chunk_index` | path string | src/lib/recorder.svelte.ts |
| `finalize_recording` | `session_id` | path string | src/lib/recorder.svelte.ts |
| `get_temp_dir` | none | string | registered only |
| `read_file_bytes` | `path` | bytes | src/routes/preview/+page.svelte |
| `create_widget_window`, `close_widget_window` | none | unit | close: src/routes/widget/+page.svelte |
| `process_recording` | `recording_path, voice_replacement, voice_id, on_event` | output path | src/routes/preview/+page.svelte |
| `test_api_key` | `api_key` | bool | src/routes/settings/+page.svelte |
| `test_local_connection` | none | bool | src/lib/voicebox.ts |
| `list_local_voices` | none | `Vec<LocalVoice>` | settings, +page, voicebox.ts |
| `check_model_status` | none | `Vec<ModelInfo>` | src/lib/voicebox.ts |
| `extract_youtube_audio` | `url, start, duration` | JSON | create-voice page |
| `poll_generation` | `generation_id` | JSON | src/lib/voicebox.ts |
| `sidecar_fetch` | `path, method, body` | string | voicebox.ts, settings, create-voice |
| `sidecar_upload` | `path, file_bytes, file_name, file_field, fields` | string | voicebox.ts, create-voice |
| `get_sidecar_status` | none | `{running, healthy, port}` | src/lib/voicebox.ts |
| `check_models_downloaded`, `download_model`, `get_models_disk_usage` | `model, on_event` for download | list / unit / u64 | registered only |
| `google_drive_connect` | `client_id, client_secret` | `DriveTokens` | settings page |
| `google_drive_disconnect` | none | unit | registered only |
| `upload_to_drive` | `access_token, file_path, on_event` | link string | preview page |

Channel payloads: `PipelineEvent` and `DriveEvent` use tag `event` and content `data`.

## Related

- [[interfaces/sidecar-http-routes]] - Sidecar HTTP routes
- [[building-blocks/tauri-core]] - Tauri core
- [[building-blocks/frontend-routes]] - Frontend routes
