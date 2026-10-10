---
id: interfaces/config-json-shape
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Config JSON Shape"
description: "Fields of the configuration object as declared in Rust and TypeScript."
domain: architecture
tags:
  - interface
  - config
  - schema
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/config.rs
  - resource: src/lib/state.svelte.ts
---
# Config JSON Shape

`AppConfig` in Rust and the matching `AppConfig` type in TypeScript use the same snake_case names.

## Fields
- `elevenlabs_api_key`: string.
- `voices`: list of `Voice { id, name, description, is_default }`.
- `output_dir`: string, default `{video dir}/VoiceOver`.
- `preferences`: `default_capture_mode`, `webcam_enabled`, `voice_replacement_enabled`.
- `google_drive`: `client_id`, `client_secret`, `access_token`, `refresh_token`, `email`, `connected`.

Declared in src-tauri/src/config.rs and src/lib/state.svelte.ts. File name `config.json` in the app data directory.

## Related
- [[building-blocks/config-store]]
- [[crosscutting/configuration]]
- [[interfaces/tauri-commands]]
