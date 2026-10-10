---
id: interfaces/tauri-commands
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Tauri commands
description: Every command registered in generate_handler, with parameters, return type and caller.
domain: architecture
tags:
  - interfaces
  - ipc
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/lib.rs
  - resource: src-tauri/src/prerequisites.rs
  - resource: src-tauri/src/config.rs
  - resource: src-tauri/src/commands/recording.rs
  - resource: src-tauri/src/commands/window.rs
  - resource: src-tauri/src/pipeline.rs
  - resource: src-tauri/src/elevenlabs.rs
  - resource: src-tauri/src/google_drive.rs
related:
  - building-blocks/backend-entry
  - interfaces/pipeline-event
  - interfaces/tauri-events
---

The thirteen commands below are listed in `tauri::generate_handler!` (src-tauri/src/lib.rs) and called with `invoke`.

| Command | Parameters | Returns | Declared in | Called from |
|---|---|---|---|---|
| `check_prerequisites` | none | `PrerequisiteStatus` | prerequisites.rs | +layout.svelte |
| `get_config` | app | `AppConfig` | config.rs | state.svelte.ts |
| `save_config` | app, `config` | unit | config.rs | state.svelte.ts |
| `save_recording_chunk` | `session_id`, `chunk: Vec<u8>`, `chunk_index: u32` | path string | commands/recording.rs | recorder.svelte.ts |
| `finalize_recording` | `session_id` | path string | commands/recording.rs | recorder.svelte.ts |
| `get_temp_dir` | none | string | commands/recording.rs | no caller in src/ |
| `create_widget_window` | app | unit | commands/window.rs | +page.svelte |
| `close_widget_window` | app | unit | commands/window.rs | widget/+page.svelte |
| `process_recording` | app, `recording_path`, `voice_replacement`, `on_event: Channel<PipelineEvent>` | output path | pipeline.rs | preview/+page.svelte |
| `test_api_key` | `api_key` | bool | elevenlabs.rs | settings/+page.svelte |
| `google_drive_connect` | `client_id`, `client_secret` | `DriveTokens` | google_drive.rs | settings/+page.svelte |
| `google_drive_disconnect` | none | unit | google_drive.rs | no caller in src/ |
| `upload_to_drive` | `access_token`, `file_path`, `on_event: Channel<DriveEvent>` | link string | google_drive.rs | preview/+page.svelte |

Errors are returned as `String`. Paths in the Called from column are under `src/` or `src/routes/` or `src/lib/`.

## Related
[[building-blocks/backend-entry]], [[interfaces/pipeline-event]], [[interfaces/tauri-events]]
