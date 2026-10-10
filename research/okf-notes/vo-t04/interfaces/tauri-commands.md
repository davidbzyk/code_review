---
id: interfaces/tauri-commands
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Tauri commands"
description: "The backend exposes 14 commands through generate_handler!, each declared with #[tauri::command] and called from the frontend by name."
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
  - resource: src-tauri/src/prerequisites.rs
  - resource: src-tauri/src/pipeline.rs
  - resource: src-tauri/src/elevenlabs.rs
  - resource: src-tauri/src/google_drive.rs
  - resource: src-tauri/src/commands/recording.rs
  - resource: src-tauri/src/commands/window.rs
relations:
  relates_to:
    - interfaces/tauri-events-and-channels
    - interfaces/config-schema
    - building-blocks/rust-app-shell
---
# Tauri commands

The command list is the boundary between the Svelte frontend and the Rust backend (registered in src-tauri/src/lib.rs).

| Command | Inputs | Returns | Declared in | Called from |
|---|---|---|---|---|
| `check_prerequisites` | none | `PrerequisiteStatus` | prerequisites.rs | src/routes/+layout.svelte |
| `get_config` | app handle | `AppConfig` | config.rs | src/lib/state.svelte.ts |
| `save_config` | `config: AppConfig` | `()` | config.rs | src/lib/state.svelte.ts |
| `save_recording_chunk` | `session_id`, `chunk: Vec<u8>`, `chunk_index: u32` | path `String` | commands/recording.rs | src/lib/recorder.svelte.ts |
| `finalize_recording` | `session_id` | path `String` | commands/recording.rs | src/lib/recorder.svelte.ts |
| `get_temp_dir` | none | `String` | commands/recording.rs | no caller in src |
| `read_file_bytes` | `path` | `Vec<u8>` | commands/recording.rs | src/routes/preview/+page.svelte |
| `create_widget_window` | app handle | `()` | commands/window.rs | no caller in src |
| `close_widget_window` | app handle | `()` | commands/window.rs | src/routes/widget/+page.svelte |
| `process_recording` | `recording_path`, `voice_replacement`, `voice_id?`, `on_event` channel | output path `String` | pipeline.rs | src/routes/preview/+page.svelte |
| `test_api_key` | `api_key` | `bool` | elevenlabs.rs | src/routes/settings/+page.svelte |
| `google_drive_connect` | `client_id`, `client_secret` | `DriveTokens` | google_drive.rs | src/routes/settings/+page.svelte |
| `google_drive_disconnect` | none | `()` | google_drive.rs | no caller in src |
| `upload_to_drive` | `access_token`, `file_path`, `on_event` channel | link `String` | google_drive.rs | src/routes/preview/+page.svelte |

All fallible commands return `Result<_, String>`. Argument names are snake_case in Rust and camelCase in the `invoke` calls (for example `sessionId`).

## Related

[[interfaces/tauri-events-and-channels]], [[interfaces/config-schema]], [[building-blocks/rust-app-shell]]
