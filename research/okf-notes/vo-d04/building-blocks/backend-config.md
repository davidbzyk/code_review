---
id: building-blocks/backend-config
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Backend config store"
description: "AppConfig structs and the get_config and save_config commands."
domain: architecture
tags:
  - backend
  - config
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
architecture_layer: building-blocks
sources:
  - resource: src-tauri/src/config.rs
related:
  - runtime/config-load-save-flow
  - crosscutting/configuration
  - crosscutting/secrets
---

# Backend config store

`src-tauri/src/config.rs` stores the app configuration as JSON in the app data directory.

## Types and functions (src-tauri/src/config.rs)
- Structs `Voice`, `Preferences`, `GoogleDrive`, `AppConfig` (serde, with defaults).
- `default_output_dir()`: the video directory (else home) joined with `VoiceOver`.
- `config_path(app)`: `app_data_dir()/config.json`, creating the directory.
- `get_config` (command): reads `config.json`; when absent, seeds from `read_static_config()` or `AppConfig::default()` and writes the file.
- `read_static_config()`: looks for `static/_config.json` above the executable and in the working directory.
- `save_config` (command): writes `config.json`, then `sync_to_static`.
- `sync_to_static`: writes `static/_config.json` when the API key is non-empty.

## Used by
src-tauri/src/pipeline.rs (`config::get_config`).

## Related

- [[runtime/config-load-save-flow]]
- [[crosscutting/configuration]]
- [[crosscutting/secrets]]
