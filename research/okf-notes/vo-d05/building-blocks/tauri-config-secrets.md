---
id: building-blocks/tauri-config-secrets
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Rust config and secrets
description: AppConfig is stored as config.json in the app data folder while secrets live in the OS keychain.
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
related:
  - crosscutting/configuration
  - crosscutting/secrets
  - building-blocks/frontend-state
---

# Rust config and secrets

`config.rs` owns the persisted settings and `secrets.rs` owns the keychain vault.

## config.rs

- Types: `AppConfig`, `Preferences`, `Voice`, `GoogleDrive`, `LocalTtsMode` (`tts` or `vc`), `WebcamPosition`.
- Defaults: provider `elevenlabs`, `local_endpoint` `http://localhost:17493`, output dir `<Videos or home>/VoiceOver`.
- `get_config` reads `config.json` under `app_data_dir`, creates it from defaults (debug builds first try `static/_config.json`), migrates plaintext secrets to the keychain once (`secrets_migrated`), then overlays keychain secrets.
- `save_config` stores secrets in the keychain, writes the sanitized config to disk, and in debug builds mirrors it to `static/_config.json` (`sync_to_static`).
- Both run inside `tokio::task::spawn_blocking`.

## secrets.rs

- One keychain entry, service `com.voiceover.app`, account `credentials`, holding a JSON `Vault` of four fields: ElevenLabs key, Drive client secret, access token, refresh token.
- `load_secrets`, `save_secrets`, `clear_secrets`, `sanitize_config`.

## Used by

- `pipeline.rs` reads config; `google_drive_disconnect` calls `clear_secrets` ([[building-blocks/tauri-google-drive]]). See [[crosscutting/configuration]] and [[crosscutting/secrets]].

## Related

- [[crosscutting/configuration]] - Configuration handling
- [[crosscutting/secrets]] - Secret handling
- [[building-blocks/frontend-state]] - Frontend state and Drive client
