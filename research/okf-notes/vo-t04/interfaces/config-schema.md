---
id: interfaces/config-schema
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Config schema"
description: "AppConfig is the JSON shape stored in config.json and mirrored by the TypeScript AppConfig type."
domain: architecture
tags:
  - interface
  - configuration
  - schema
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/config.rs
  - resource: src/lib/state.svelte.ts
relations:
  relates_to:
    - building-blocks/rust-config
    - building-blocks/frontend-state
    - crosscutting/configuration
---
# Config schema

The same field names appear in the Rust structs and the TypeScript types.

## Fields

| Field | Type | Default (Rust) |
|---|---|---|
| `elevenlabs_api_key` | string | empty |
| `voices` | list of `Voice { id, name, description, is_default }` | empty |
| `output_dir` | string | `<Videos or home>/VoiceOver` |
| `preferences.default_capture_mode` | string | `fullscreen` |
| `preferences.webcam_enabled` | bool | false |
| `preferences.voice_replacement_enabled` | bool | true |
| `google_drive.client_id`, `client_secret`, `access_token`, `refresh_token`, `email` | string | empty |
| `google_drive.connected` | bool | false |
| `google_drive.expires_at` | u64 / number, Unix seconds | 0 |

Declared in src-tauri/src/config.rs (`AppConfig`, `Preferences`, `GoogleDrive`, `Voice`) and src/lib/state.svelte.ts (`AppConfig`, `GoogleDrive`, `Voice`). `DriveTokens` in src-tauri/src/google_drive.rs carries the token subset returned by `google_drive_connect`.

## Related

[[building-blocks/rust-config]], [[building-blocks/frontend-state]], [[crosscutting/configuration]]
