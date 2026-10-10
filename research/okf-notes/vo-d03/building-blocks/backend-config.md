---
id: building-blocks/backend-config
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Backend config module"
description: "Config structs, JSON file in the app data directory, and the static config sync."
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
relations:
  relates_to:
    - crosscutting/configuration
    - crosscutting/secrets
    - runtime/load-config
---

# Backend config module

`src-tauri/src/config.rs` defines `AppConfig` and the commands that read and write it.

## Types

`Voice` (`id`, `name`, `description`, `is_default`), `Preferences` (`default_capture_mode` default `fullscreen`, `webcam_enabled` false, `voice_replacement_enabled` true), `GoogleDrive` (client id and secret, access and refresh tokens, `email`, `connected`, `expires_at`), `AppConfig` (`elevenlabs_api_key`, `voices`, `output_dir`, `preferences`, `google_drive`). Fields use `#[serde(default)]`; `default_output_dir()` is the video directory (or home) joined with `VoiceOver`.

## Functions

- `config_path(app)`: `app_data_dir()/config.json`, creating the directory.
- `get_config` (command): reads and parses the file; when absent, seeds from `read_static_config()` or defaults and writes the file.
- `read_static_config()`: looks for `static/_config.json` in ancestors of the executable and in the working directory.
- `save_config` (command): writes pretty JSON, then `sync_to_static`.
- `sync_to_static(config)`: returns early when the API key is empty; otherwise writes `static/_config.json` with the key and Drive secrets and tokens blanked.

## Used by

`src-tauri/src/pipeline.rs` calls `config::get_config`.

## Related

- [crosscutting/configuration](../crosscutting/configuration.md)
- [crosscutting/secrets](../crosscutting/secrets.md)
- [runtime/load-config](../runtime/load-config.md)
- [building-blocks/backend-pipeline](./backend-pipeline.md)
