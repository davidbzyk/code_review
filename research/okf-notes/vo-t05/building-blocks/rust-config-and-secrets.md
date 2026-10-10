---
id: building-blocks/rust-config-and-secrets
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Rust Config and Secrets
description: The persisted AppConfig in config.json and the keychain vault that holds its secrets.
domain: architecture
tags:
  - building-block
  - rust
  - config
  - secrets
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/config.rs
  - resource: src-tauri/src/secrets.rs
related:
  - crosscutting/configuration
  - crosscutting/secrets
  - runtime/config-load-save
  - building-blocks/frontend-state-and-config
---

# Rust Config and Secrets

`config.rs` defines `AppConfig` and the `get_config` and `save_config` commands; `secrets.rs` moves four secret fields to the keychain.

## config.rs

- `AppConfig` fields: `elevenlabs_api_key`, `voices`, `output_dir`, `preferences`, `google_drive`, `secrets_migrated`, `provider` (default `elevenlabs`), `local_endpoint`, `local_voice_profile_id`, `local_tts_mode`.
- `LocalTtsMode` is `tts` or `vc`; `WebcamPosition` is `bottom-left` or `bottom-right`.
- The file is `config.json` in the app data dir (`config_path`).
- `read_static_config` reads `static/_config.json`, compiled only with `debug_assertions`; `sync_to_static` writes it in debug builds.

## secrets.rs

- Service `com.voiceover.app`, account `credentials`; one JSON `Vault` with four fields.
- `load_secrets`, `save_secrets`, `clear_secrets`, `sanitize_config`.
- `read_vault` returns `None` on keychain errors other than `NoEntry`.

## Used by

`pipeline.rs` calls `config::get_config`; `google_drive_disconnect` calls `clear_secrets`.

## Related

- [Configuration](../crosscutting/configuration.md)
- [Secrets](../crosscutting/secrets.md)
- [Flow: Load and Save Config](../runtime/config-load-save.md)
- [Frontend State and Config](./frontend-state-and-config.md)
