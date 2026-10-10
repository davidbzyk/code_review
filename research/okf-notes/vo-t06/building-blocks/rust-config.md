---
id: building-blocks/rust-config
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Rust Config"
description: "Persistent app configuration stored as config.json in the app data directory."
domain: architecture
tags:
  - building-blocks
  - rust
  - configuration
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/config.rs
relations:
  relates_to:
    - building-blocks/rust-secrets
    - crosscutting/configuration
    - runtime/config-load-save
---

The config module defines `AppConfig` and the `get_config` and `save_config` commands.

## Facts

- Types: `Voice`, `WebcamPosition` (`bottom-left`, `bottom-right`), `Preferences`, `GoogleDrive`, `AppConfig` (`src-tauri/src/config.rs`).
- `deserialize_webcam_position` maps unknown strings to the default `bottom-right`.
- `default_output_dir()` is `<video dir or home>/VoiceOver`, or `~/VoiceOver` when neither exists.
- `config_path` is `app_data_dir()/config.json`; the directory is created when missing.
- `get_config`: reads the file when it exists. Otherwise it calls `read_static_config()` (debug builds only, reads `static/_config.json`), falls back to `AppConfig::default()` and writes the file.
- `get_config` migration: when `secrets_migrated` is false and any secret field is non-empty, it calls `secrets::save_secrets`, strips secrets with `secrets::sanitize_config`, sets `secrets_migrated = true` and rewrites the file.
- `get_config` ends with `secrets::load_secrets`, so keychain values replace the file values.
- `save_config` saves secrets to the keychain, writes the sanitized config to `config.json`, then calls `sync_to_static` (debug builds write `static/_config.json`; release builds do nothing).
- Callers: `src/lib/state.svelte.ts` through `tauriInvoke`; `pipeline::process_recording` calls `config::get_config`.

## Related

- [Rust secrets](rust-secrets.md)
- [Configuration](../crosscutting/configuration.md)
- [Config load and save flow](../runtime/config-load-save.md)
