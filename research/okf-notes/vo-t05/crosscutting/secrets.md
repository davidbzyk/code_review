---
id: crosscutting/secrets
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Secrets
description: Handling of the ElevenLabs key and Google Drive credentials.
domain: architecture
tags:
  - crosscutting
  - secrets
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/secrets.rs
  - resource: src-tauri/src/config.rs
  - resource: src/lib/state.svelte.ts
  - resource: vite.config.ts
  - resource: src-tauri/src/google_drive.rs
related:
  - building-blocks/rust-config-and-secrets
  - runtime/config-load-save
  - runtime/google-drive-connect-upload
---

# Secrets

Four values are secrets: the ElevenLabs API key and the Google Drive client secret, access token and refresh token.

## Facts

- They are stored as one JSON string in the keychain entry service `com.voiceover.app`, account `credentials` (src-tauri/src/secrets.rs).
- `sanitize_config` blanks them before `config.json` is written (src-tauri/src/config.rs `save_config`).
- `get_config` migrates old plaintext values into the keychain once, guarded by `secrets_migrated`.
- `sanitizeForStorage` blanks them before writing `localStorage` (src/lib/state.svelte.ts).
- In debug builds `sync_to_static` writes the config to `static/_config.json`; `stripConfigPlugin` deletes `build/_config.json` from production builds (vite.config.ts).
- `google_drive_disconnect` calls `clear_secrets`, deleting the keychain entry.
- The ElevenLabs key is sent in the `xi-api-key` header (src-tauri/src/elevenlabs.rs).
- Logging masks the key to its last 4 characters in `test_api_key`.
- `.gitignore` lists `.env` files.

## Used by

`config.rs`, `google_drive.rs`, `elevenlabs.rs`, `pipeline.rs`.

## Related

- [Rust Config and Secrets](../building-blocks/rust-config-and-secrets.md)
- [Flow: Load and Save Config](../runtime/config-load-save.md)
- [Flow: Connect and Upload to Google Drive](../runtime/google-drive-connect-upload.md)
