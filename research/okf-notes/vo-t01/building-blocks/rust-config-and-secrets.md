---
id: building-blocks/rust-config-and-secrets
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Rust Config and Secrets
description: The AppConfig model, its JSON file, and the keychain vault.
domain: architecture
tags:
  - building-block
  - rust
  - config
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/config.rs
  - resource: src-tauri/src/secrets.rs
relations:
  relates_to:
    - crosscutting/configuration
    - crosscutting/secrets
    - interfaces/tauri-commands-app
    - runtime/config-load-and-save
---
# Rust Config and Secrets

These modules define the settings model and keep secrets out of the settings file.

## `config.rs`

- Types: `AppConfig`, `Voice`, `Preferences`, `GoogleDrive`, `WebcamPosition`, `LocalTtsMode` (`tts`, `vc`).
- `config_path` returns `config.json` in the app data dir.
- Commands `get_config` and `save_config` run on `spawn_blocking`.
- `read_static_config` reads `static/_config.json` in debug builds only; the release build returns `None`.
- `sync_to_static` writes the sanitized config for the dev server.

## `secrets.rs`

- `Vault` holds `elevenlabs_api_key`, `google_drive_client_secret`, `google_drive_access_token`, `google_drive_refresh_token` as one JSON string in a keychain entry (service `com.voiceover.app`, account `credentials`).
- `load_secrets`, `save_secrets`, `clear_secrets`, `sanitize_config`.

## Used by

`pipeline.rs`, `library.rs`, `google_drive.rs`.

## Related

- [Configuration](../crosscutting/configuration.md)
- [Secrets](../crosscutting/secrets.md)
- [Tauri Commands: Config, Recording, Library, Drive, Window](../interfaces/tauri-commands-app.md)
- [Flow: Config Load and Save](../runtime/config-load-and-save.md)
