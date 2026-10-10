---
id: interfaces/tauri-commands-app
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Tauri Commands: Config, Recording, Library, Drive, Window
description: Command names, inputs, outputs and call sites for the non-TTS commands.
domain: architecture
tags:
  - interface
  - tauri
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/lib.rs
  - resource: src-tauri/src/config.rs
  - resource: src-tauri/src/commands/recording.rs
  - resource: src-tauri/src/library.rs
  - resource: src-tauri/src/google_drive.rs
  - resource: src-tauri/src/commands/window.rs
  - resource: src-tauri/src/prerequisites.rs
  - resource: src-tauri/src/pipeline.rs
  - resource: src-tauri/src/elevenlabs.rs
relations:
  relates_to:
    - interfaces/tauri-commands-tts
    - interfaces/events-and-channels
    - building-blocks/rust-app-shell
---
# Tauri Commands: Config, Recording, Library, Drive, Window

These commands are registered in `generate_handler!` in `src-tauri/src/lib.rs`.

| Command | Inputs | Output | Called from |
|---|---|---|---|
| `check_prerequisites` | none | `PrerequisiteStatus` | `src/routes/+layout.svelte` |
| `get_config` | none | `AppConfig` | `src/lib/state.svelte.ts` |
| `save_config` | `config` | unit | `src/lib/state.svelte.ts` |
| `save_recording_chunk` | `session_id`, `chunk`, `chunk_index` | path string | `src/lib/recorder.svelte.ts` |
| `finalize_recording` | `session_id` | path string | `src/lib/recorder.svelte.ts` |
| `get_temp_dir` | none | string | no call under `src/` |
| `read_file_bytes` | `path` | bytes | `RecordingCard.svelte`, preview page |
| `create_widget_window` | none | unit | no call under `src/` |
| `close_widget_window` | none | unit | `src/routes/widget/+page.svelte` |
| `process_recording` | `recording_path`, `voice_replacement`, `voice_id`, `on_event` | output path | preview page |
| `test_api_key` | `api_key` | bool | settings page |
| `google_drive_connect` | `client_id`, `client_secret` | `DriveTokens` | settings page |
| `upload_to_drive` | `access_token`, `file_path`, `on_event` | link string | `RecordingCard.svelte`, preview page |
| `google_drive_disconnect` | none | unit | no call under `src/` |
| `list_recordings` | none | `Vec<RecordingInfo>` | `src/lib/library.svelte.ts` |
| `generate_thumbnail` | `file_path` | path string | `RecordingCard.svelte` |
| `delete_recording` | `file_path` | unit | `src/lib/library.svelte.ts` |
| `rename_recording` | `file_path`, `new_name` | `RecordingInfo` | `src/lib/library.svelte.ts` |
| `open_in_system`, `reveal_in_finder` | `path` | unit | `src/lib/library.svelte.ts` |

## Related

- [Tauri Commands: Local TTS, Models, Sidecar](tauri-commands-tts.md)
- [Events and Channels](events-and-channels.md)
- [Rust App Shell](../building-blocks/rust-app-shell.md)
