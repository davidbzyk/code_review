---
id: crosscutting/secrets
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Secrets"
description: "How credentials are kept out of config files and local storage."
domain: architecture
tags:
  - crosscutting
  - secrets
  - security
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/secrets.rs
  - resource: src-tauri/src/config.rs
  - resource: src/lib/state.svelte.ts
  - resource: src-tauri/src/google_drive.rs
relations:
  relates_to:
    - building-blocks/rust-secrets
    - crosscutting/configuration
---

Four values are secret: the ElevenLabs key and the Google client secret, access token and refresh token.

## Facts

- Stored in one keychain entry (`com.voiceover.app`, `credentials`) by `save_secrets` (`src-tauri/src/secrets.rs`).
- `sanitize_config` blanks them before `config.json` is written (`src-tauri/src/config.rs`).
- `sanitizeForStorage` blanks them before `localStorage` is written (`src/lib/state.svelte.ts`).
- `get_config` moves plaintext secrets from an older `config.json` to the keychain and records `secrets_migrated`.
- `google_drive_disconnect` deletes the keychain entry.
- `google_drive_connect` uses PKCE and a random `state` check (`src-tauri/src/google_drive.rs`).
- `read_file_bytes` and `validate_session_id` restrict file access (`src-tauri/src/commands/recording.rs`).
- `log::info!` in `test_api_key` prints only the last four key characters; the settings page logs a masked key.
- `src-tauri/tauri.conf.json` sets a Content Security Policy.

## Related

- [Rust secrets](../building-blocks/rust-secrets.md)
- [Configuration](configuration.md)
