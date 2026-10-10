---
id: building-blocks/backend-config-and-secrets
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Backend Config and Secrets"
description: "The config file model and the keychain vault."
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
  - resource: src-tauri/src/secrets.rs
related:
  - crosscutting/configuration
  - crosscutting/secrets
  - runtime/config-load-and-save
---
# Backend Config and Secrets

This block reads and writes `config.json` and keeps secrets in the operating system keychain.

## src-tauri/src/config.rs
Structs `Voice`, `Preferences`, `GoogleDrive`, `AppConfig`; enum `WebcamPosition`; commands `get_config` and `save_config`; private `config_path`, `default_output_dir`, `read_static_config`, `sync_to_static`.

## src-tauri/src/secrets.rs
Private struct `Vault` (ElevenLabs key and three Google values); `load_secrets`, `save_secrets`, `clear_secrets`, `sanitize_config`. Constants `SERVICE = "com.voiceover.app"` and `ACCOUNT = "credentials"`.

## Used by
`pipeline::process_recording` calls `config::get_config`; `google_drive_disconnect` calls `secrets::clear_secrets`.

## Related
- [Configuration](../crosscutting/configuration.md)
- [Secrets](../crosscutting/secrets.md)
- [Config Load and Save](../runtime/config-load-and-save.md)
