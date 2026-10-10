---
id: building-blocks/backend-config
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Rust config module
description: AppConfig structs and the get_config and save_config commands.
domain: architecture
tags:
  - building-block
  - backend
  - config
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/config.rs
related:
  - interfaces/config-data-shape
  - runtime/config-load-and-save
  - crosscutting/configuration-and-secrets
---

src-tauri/src/config.rs defines the persisted settings and reads and writes `config.json` in the app data directory.

## Types
`Voice`, `Preferences` (default `fullscreen`, webcam false, voice replacement true), `GoogleDrive`, `AppConfig` with serde defaults. `default_output_dir()` is the user video directory, else home, joined with `VoiceOver`.

## Functions
- `config_path(app)`: `app_data_dir()/config.json`, creating the directory.
- `get_config` (command): reads and parses the file; when missing, writes and returns defaults.
- `save_config` (command): writes pretty JSON, then calls `sync_to_static`.
- `sync_to_static(config)`: writes `_config.json` into a `static` directory found by walking up from the executable, else `./static`, with `elevenlabs_api_key`, Drive client id, secret and tokens blanked.

## Called by
`pipeline::process_recording` (reads config) and the frontend through [[interfaces/tauri-commands]].

## Related
[[interfaces/config-data-shape]], [[runtime/config-load-and-save]], [[crosscutting/configuration-and-secrets]]
