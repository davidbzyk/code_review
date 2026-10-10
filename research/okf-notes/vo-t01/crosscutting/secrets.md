---
id: crosscutting/secrets
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Secrets
description: How API keys and OAuth tokens are stored.
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
  - resource: vite.config.ts
relations:
  relates_to:
    - crosscutting/configuration
    - runtime/config-load-and-save
    - building-blocks/rust-config-and-secrets
---
# Secrets

Four secret values are kept in one OS keychain entry and removed from files.

## Facts

- `Vault` fields: `elevenlabs_api_key`, `google_drive_client_secret`, `google_drive_access_token`, `google_drive_refresh_token` (`src-tauri/src/secrets.rs`).
- Entry: service `com.voiceover.app`, account `credentials`, stored as a JSON string.
- `read_vault` returns `None` on keychain errors other than a missing entry; `load_secrets` then keeps the config as is.
- `sanitize_config` blanks the four fields before `save_config` writes the file.
- `get_config` migrates pre-keychain files once, then sets `secrets_migrated`.
- `google_drive_disconnect` calls `clear_secrets`, which deletes the credential.
- The webview strips secrets before writing `localStorage` (`sanitizeForStorage`).
- The log line for the ElevenLabs key shows the last four characters only (`test_api_key` in `src-tauri/src/elevenlabs.rs`).
- `stripConfigPlugin` removes `build/_config.json` from production builds (`vite.config.ts`).

## Related

- [Configuration](configuration.md)
- [Flow: Config Load and Save](../runtime/config-load-and-save.md)
- [Rust Config and Secrets](../building-blocks/rust-config-and-secrets.md)
