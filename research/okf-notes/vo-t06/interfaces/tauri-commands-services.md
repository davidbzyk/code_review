---
id: interfaces/tauri-commands-services
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Tauri Commands, Services"
description: "Commands for the pipeline, ElevenLabs key test and Google Drive."
domain: architecture
tags:
  - interfaces
  - tauri
  - commands
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/pipeline.rs
  - resource: src-tauri/src/elevenlabs.rs
  - resource: src-tauri/src/google_drive.rs
relations:
  relates_to:
    - interfaces/tauri-commands-core
    - interfaces/tauri-events
    - interfaces/external-http-apis
---

These commands call outside services or ffmpeg; all are registered in `src-tauri/src/lib.rs`.

| Command | Inputs | Output | Declared in | Called from |
|---|---|---|---|---|
| `process_recording` | `recordingPath`, `voiceReplacement`, `voiceId` (optional), `onEvent` channel of `PipelineEvent` | output MP4 path | `pipeline.rs` | `src/routes/preview/+page.svelte` |
| `test_api_key` | `apiKey` | `bool` | `elevenlabs.rs` | `src/routes/settings/+page.svelte` |
| `google_drive_connect` | `clientId`, `clientSecret` | `DriveTokens` | `google_drive.rs` | `src/routes/settings/+page.svelte` |
| `google_drive_disconnect` | none | unit | `google_drive.rs` | no call in `src/` |
| `upload_to_drive` | `accessToken`, `filePath`, `onEvent` channel of `DriveEvent` | web view link | `google_drive.rs` | `src/routes/preview/+page.svelte` |

Argument names are camelCase on the JavaScript side and snake_case in Rust, as the `invoke` calls show. All five return `Result<_, String>`.

`DriveTokens` fields: `access_token`, `refresh_token`, `email`, `connected`, `expires_at`.

## Related

- [Tauri commands, core](tauri-commands-core.md)
- [Tauri events and channels](tauri-events.md)
- [External HTTP APIs](external-http-apis.md)
