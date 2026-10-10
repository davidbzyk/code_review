---
id: building-blocks/rust-config-and-secrets
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Rust config and secrets"
description: "The AppConfig model stored as config.json and the keychain vault for secrets."
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
  - crosscutting/secrets-handling
  - runtime/config-load-and-save
---
# Rust config and secrets

`config.rs` persists the non-secret settings and `secrets.rs` keeps credentials in the OS keychain.

## config.rs

- Types `Voice`, `WebcamPosition`, `Preferences`, `GoogleDrive`, `AppConfig` (serde, with defaults).
- `default_output_dir` (`<video dir or home>/VoiceOver`), `default_provider` (`elevenlabs`), `default_local_endpoint`.
- `config_path` is `<app data dir>/config.json`.
- Commands `get_config` and `save_config` run file work on `spawn_blocking`.
- Debug builds only: `read_static_config` and `sync_to_static` use `static/_config.json`.

## secrets.rs

- Keychain entry service `com.voiceover.app`, account `credentials`; one JSON `Vault` with `elevenlabs_api_key`, `google_drive_client_secret`, `google_drive_access_token`, `google_drive_refresh_token`.
- `load_secrets`, `save_secrets`, `clear_secrets`, `sanitize_config`.

## Callers

`pipeline.rs` calls `get_config`; `google_drive_disconnect` calls `clear_secrets`; the frontend calls both commands through `appState`.

## Related

- [[crosscutting/configuration]]
- [[crosscutting/secrets-handling]]
- [[runtime/config-load-and-save]]
