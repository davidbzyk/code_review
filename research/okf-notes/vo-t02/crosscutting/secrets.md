---
id: crosscutting/secrets
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Secrets"
description: "How credentials are stored and removed from files."
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
  - resource: src-tauri/src/google_drive.rs
related:
  - crosscutting/configuration
  - building-blocks/backend-config-and-secrets
---
# Secrets

Secrets go to one keychain entry and are blanked in files.

## Facts
- One JSON `Vault` under service `com.voiceover.app`, account `credentials` (src-tauri/src/secrets.rs).
- Vault fields: ElevenLabs key, Google client secret, access token, refresh token.
- `sanitize_config` clears those four fields before `config.json` is written (src-tauri/src/config.rs).
- `read_vault` returns `None` on a keychain error other than `NoEntry`, and `load_secrets` then leaves the config unchanged.
- `sanitizeForStorage` blanks the same four fields before the localStorage write (src/lib/state.svelte.ts).
- `google_drive_disconnect` calls `clear_secrets`, which deletes the credential entry (src-tauri/src/google_drive.rs).
- In debug builds `save_config` passes the already sanitized copy to `sync_to_static`, which writes `static/_config.json`.

## Related
- [Configuration](./configuration.md)
- [Backend Config and Secrets](../building-blocks/backend-config-and-secrets.md)
