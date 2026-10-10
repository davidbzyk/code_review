---
id: interfaces/config-data-shape
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Config data shape
description: Fields of AppConfig as declared in Rust and in TypeScript.
domain: architecture
tags:
  - interfaces
  - config
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/config.rs
  - resource: src/lib/state.svelte.ts
related:
  - building-blocks/backend-config
  - building-blocks/frontend-state-and-logging
  - crosscutting/configuration-and-secrets
---

`AppConfig` is declared in src-tauri/src/config.rs and mirrored as a type in src/lib/state.svelte.ts.

| Field | Type | Notes |
|---|---|---|
| `elevenlabs_api_key` | string | default empty |
| `voices` | list of `Voice` | `id`, `name`, `description`, `is_default` |
| `output_dir` | string | default from `default_output_dir()` |
| `preferences` | object | `default_capture_mode`, `webcam_enabled`, `voice_replacement_enabled` |
| `google_drive` | object | `client_id`, `client_secret`, `access_token`, `refresh_token`, `email`, `connected`, `expires_at` (Unix seconds) |

Rust fields carry `#[serde(default)]`, so missing keys take defaults when parsing.

## Related
[[building-blocks/backend-config]], [[building-blocks/frontend-state-and-logging]], [[crosscutting/configuration-and-secrets]]
