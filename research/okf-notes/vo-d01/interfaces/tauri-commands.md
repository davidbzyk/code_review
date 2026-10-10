---
id: interfaces/tauri-commands
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Tauri Commands"
description: "Every command registered in the handler list, with parameters and returns."
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
---
# Tauri Commands

The 13 commands are listed in `generate_handler!` in src-tauri/src/lib.rs.

| Command | Inputs | Returns | Caller |
|---|---|---|---|
| `check_prerequisites` | none | `PrerequisiteStatus` | src/routes/+layout.svelte |
| `get_config` | none | `AppConfig` | src/lib/state.svelte.ts |
| `save_config` | `config` | unit | src/lib/state.svelte.ts |
| `save_recording_chunk` | `sessionId`, `chunk`, `chunkIndex` | path string | src/lib/recorder.svelte.ts |
| `finalize_recording` | `sessionId` | path string | src/lib/recorder.svelte.ts |
| `get_temp_dir` | none | string | no caller found in src |
| `create_widget_window` | none | unit | src/routes/+page.svelte |
| `close_widget_window` | none | unit | src/routes/widget/+page.svelte |
| `process_recording` | `recordingPath`, `voiceReplacement`, `onEvent` | output path | src/routes/preview/+page.svelte |
| `test_api_key` | `apiKey` | bool | src/routes/settings/+page.svelte |
| `google_drive_connect` | `clientId`, `clientSecret` | `DriveTokens` | src/routes/settings/+page.svelte |
| `google_drive_disconnect` | none | unit | no caller found in src |
| `upload_to_drive` | `accessToken`, `filePath`, `onEvent` | link string | src/routes/preview/+page.svelte |

Declaring files are the module files under src-tauri/src.

## Related
- [[interfaces/pipeline-channel-events]]
- [[building-blocks/tauri-shell]]
- [[interfaces/config-json-shape]]
