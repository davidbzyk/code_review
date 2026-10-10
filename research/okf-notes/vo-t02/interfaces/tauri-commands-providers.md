---
id: interfaces/tauri-commands-providers
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Tauri Commands: Config, Providers and Drive"
description: "Commands for configuration, speech providers and Google Drive."
domain: architecture
tags:
  - interfaces
  - tauri
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/config.rs
  - resource: src-tauri/src/elevenlabs.rs
  - resource: src-tauri/src/local_tts.rs
  - resource: src-tauri/src/google_drive.rs
  - resource: src/lib/voicebox.ts
  - resource: src/lib/state.svelte.ts
  - resource: src/routes/settings/+page.svelte
  - resource: src/routes/preview/+page.svelte
related:
  - interfaces/tauri-commands-recording-and-pipeline
  - interfaces/events-and-channels
  - interfaces/external-http-apis
---
# Tauri Commands: Config, Providers and Drive

These commands are registered in src-tauri/src/lib.rs.

| Command | Inputs | Returns | Declared in | Called from |
|---|---|---|---|---|
| `get_config` | `app` | `AppConfig` | config.rs | src/lib/state.svelte.ts |
| `save_config` | `app`, `config: AppConfig` | `()` | config.rs | src/lib/state.svelte.ts |
| `test_api_key` | `api_key` | `bool` | elevenlabs.rs | src/routes/settings/+page.svelte |
| `test_local_connection` | `endpoint` | `bool` | local_tts.rs | settings route, src/lib/voicebox.ts |
| `list_local_voices` | `endpoint` | `Vec<LocalVoice>` | local_tts.rs | settings route, src/lib/voicebox.ts |
| `check_model_status` | `endpoint` | `Vec<ModelInfo>` | local_tts.rs | src/lib/voicebox.ts |
| `voicebox_fetch` | `url`, `method`, `body`, `content_type` | response text | local_tts.rs | src/lib/voicebox.ts |
| `voicebox_upload` | `url`, `file_bytes`, `file_name`, `file_field`, `fields` | response text | local_tts.rs | src/lib/voicebox.ts |
| `google_drive_connect` | `client_id`, `client_secret` | `DriveTokens` | google_drive.rs | settings route |
| `google_drive_disconnect` | none | `()` | google_drive.rs | no caller in src |
| `upload_to_drive` | `access_token`, `file_path`, `on_event: Channel<DriveEvent>` | link `String` | google_drive.rs | preview route |

All Rust return types are `Result<_, String>`. Settings and preview routes are under src/routes/.

## Related
- [Tauri Commands: Recording and Pipeline](./tauri-commands-recording-and-pipeline.md)
- [Events and Channels](./events-and-channels.md)
- [External HTTP APIs](./external-http-apis.md)
