---
id: interfaces/tauri-commands
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Tauri commands"
description: "The 14 commands registered in invoke_handler: parameters, results and callers."
domain: architecture
tags:
  - interface
  - tauri
  - ipc
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/lib.rs
  - resource: src-tauri/src/config.rs
  - resource: src-tauri/src/commands/recording.rs
  - resource: src-tauri/src/commands/window.rs
  - resource: src-tauri/src/pipeline.rs
  - resource: src-tauri/src/prerequisites.rs
  - resource: src-tauri/src/elevenlabs.rs
  - resource: src-tauri/src/google_drive.rs
relations:
  relates_to:
    - interfaces/pipeline-events
    - building-blocks/backend-entry
---

# Tauri commands

`generate_handler!` in `src-tauri/src/lib.rs` registers these commands; the frontend calls them through `invoke`.

| Command | Inputs | Returns | Declared in | Called from |
|---|---|---|---|---|
| `check_prerequisites` | none | `PrerequisiteStatus` | `prerequisites.rs` | `+layout.svelte` |
| `get_config` | app handle | `AppConfig` | `config.rs` | `state.svelte.ts` |
| `save_config` | `config: AppConfig` | unit | `config.rs` | `state.svelte.ts` |
| `save_recording_chunk` | `session_id`, `chunk: Vec<u8>`, `chunk_index: u32` | path string | `commands/recording.rs` | `recorder.svelte.ts` |
| `finalize_recording` | `session_id` | path string | `commands/recording.rs` | `recorder.svelte.ts` |
| `get_temp_dir` | none | string | `commands/recording.rs` | no caller found in `src/` |
| `read_file_bytes` | `path` | `Vec<u8>` | `commands/recording.rs` | `preview/+page.svelte` |
| `create_widget_window` | app handle | unit | `commands/window.rs` | no caller found in `src/` |
| `close_widget_window` | app handle | unit | `commands/window.rs` | `widget/+page.svelte` |
| `process_recording` | `recording_path`, `voice_replacement`, `voice_id?`, `on_event: Channel<PipelineEvent>` | output path | `pipeline.rs` | `preview/+page.svelte` |
| `test_api_key` | `api_key` | bool | `elevenlabs.rs` | `settings/+page.svelte` |
| `google_drive_connect` | `client_id`, `client_secret` | `DriveTokens` | `google_drive.rs` | `settings/+page.svelte` |
| `google_drive_disconnect` | none | unit | `google_drive.rs` | no caller found in `src/` |
| `upload_to_drive` | `access_token`, `file_path`, `on_event: Channel<DriveEvent>` | share link | `google_drive.rs` | `preview/+page.svelte` |

All results are `Result<_, String>` except `get_temp_dir`. Tauri converts snake_case parameters to camelCase for JavaScript (for example `sessionId`).

## Related

- [interfaces/pipeline-events](./pipeline-events.md)
- [building-blocks/backend-entry](../building-blocks/backend-entry.md)
- [building-blocks/frontend-state](../building-blocks/frontend-state.md)
