---
id: crosscutting/secrets-handling
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Secrets handling"
description: "How API keys and OAuth tokens are stored, stripped and masked."
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
  - resource: src-tauri/src/elevenlabs.rs
  - resource: src/routes/settings/+page.svelte
related:
  - crosscutting/configuration
  - runtime/google-drive-connect-and-upload
  - building-blocks/rust-config-and-secrets
---
# Secrets handling

Four secrets go to the OS keychain and are blanked in every stored copy.

## Facts

- The keychain holds one JSON entry with the ElevenLabs key and the Drive client secret, access token and refresh token (src-tauri/src/secrets.rs).
- `sanitize_config` empties those four fields before `config.json` is written (src-tauri/src/config.rs `save_config`).
- `sanitizeForStorage` empties the same fields before writing to localStorage (src/lib/state.svelte.ts).
- `get_config` migrates old plaintext values once, guarded by `secrets_migrated`.
- If the keychain read fails, `load_secrets` logs a warning and keeps the config unchanged.
- `google_drive_disconnect` deletes the keychain entry through `clear_secrets`.
- `test_api_key` logs only the last four characters; the settings page masks as first six plus last four.
- The Drive upload code does not change sharing; its comments say files stay private.

## Used by

config.rs, google_drive.rs, the settings page and the preview page.

## Related

- [[crosscutting/configuration]]
- [[runtime/google-drive-connect-and-upload]]
- [[building-blocks/rust-config-and-secrets]]
