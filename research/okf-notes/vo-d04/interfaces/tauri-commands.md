---
id: interfaces/tauri-commands
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Tauri commands"
description: "The 14 commands registered in invoke_handler, with parameters, returns, declaring and calling files."
domain: architecture
tags:
  - interfaces
  - tauri
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
architecture_layer: interfaces
sources:
  - resource: src-tauri/src/lib.rs
  - resource: src-tauri/src/config.rs
  - resource: src-tauri/src/prerequisites.rs
  - resource: src-tauri/src/commands/recording.rs
  - resource: src-tauri/src/commands/window.rs
  - resource: src-tauri/src/pipeline.rs
  - resource: src-tauri/src/elevenlabs.rs
  - resource: src-tauri/src/google_drive.rs
related:
  - interfaces/pipeline-events
  - building-blocks/backend-shell
  - interfaces/tauri-capabilities
---

# Tauri commands

The webview calls Rust through `invoke(name, args)`; the list is in `generate_handler!` (src-tauri/src/lib.rs).

| Command | Inputs | Returns | Called from |
|---|---|---|---|
| check_prerequisites | none | PrerequisiteStatus | +layout.svelte |
| get_config | none | AppConfig | state.svelte.ts |
| save_config | config | unit | state.svelte.ts |
| save_recording_chunk | session_id, chunk, chunk_index | path String | recorder.svelte.ts |
| finalize_recording | session_id | path String | recorder.svelte.ts |
| get_temp_dir | none | String | no caller in src/ |
| read_file_bytes | path | Vec<u8> | preview/+page.svelte |
| create_widget_window | none | unit | no caller in src/ |
| close_widget_window | none | unit | widget/+page.svelte |
| process_recording | recording_path, voice_replacement, voice_id, on_event | output path String | preview/+page.svelte |
| test_api_key | api_key | bool | settings/+page.svelte |
| google_drive_connect | client_id, client_secret | DriveTokens | settings/+page.svelte |
| google_drive_disconnect | none | unit | no caller in src/ |
| upload_to_drive | access_token, file_path, on_event | link String | preview/+page.svelte |

Declaring files: config.rs, prerequisites.rs, commands/recording.rs, commands/window.rs, pipeline.rs, elevenlabs.rs, google_drive.rs (all under src-tauri/src/). Results are `Result<_, String>`.

## Related

- [[interfaces/pipeline-events]]
- [[building-blocks/backend-shell]]
- [[interfaces/tauri-capabilities]]
