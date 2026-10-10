---
id: crosscutting/configuration
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Configuration"
description: "Where settings live and how defaults apply."
domain: architecture
tags:
  - crosscutting
  - config
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/config.rs
  - resource: src/lib/state.svelte.ts
  - resource: vite.config.ts
  - resource: .gitignore
related:
  - runtime/config-load-and-save
  - building-blocks/backend-config-and-secrets
  - crosscutting/secrets
---
# Configuration

Settings are a single `AppConfig` shape on both sides of the bridge.

## Facts
- Rust `AppConfig` fields: `elevenlabs_api_key`, `voices`, `output_dir`, `preferences`, `google_drive`, `secrets_migrated`, `provider`, `local_endpoint`, `local_voice_profile_id` (src-tauri/src/config.rs). Fields carry `#[serde(default)]`.
- Defaults: provider `elevenlabs`, endpoint `http://localhost:17493`, output folder `VoiceOver` under the video or home directory, capture mode `fullscreen`.
- File location: `config.json` in `app_data_dir` (`config_path`).
- TypeScript `AppConfig` mirrors the shape (src/lib/state.svelte.ts).
- Debug builds also read `static/_config.json` on first run and write it on save (`read_static_config`, `sync_to_static`); `.gitignore` lists `static/_config.json`.
- `stripConfigPlugin` deletes `build/_config.json` from production builds (vite.config.ts).
- `webcam_position` falls back to `bottom-right` on an unknown value (`deserialize_webcam_position`).

## Used by
`pipeline.rs`, `settings` route, `state.svelte.ts`.

## Related
- [Config Load and Save](../runtime/config-load-and-save.md)
- [Backend Config and Secrets](../building-blocks/backend-config-and-secrets.md)
- [Secrets](./secrets.md)
