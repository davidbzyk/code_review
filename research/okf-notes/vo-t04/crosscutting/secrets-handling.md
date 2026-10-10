---
id: crosscutting/secrets-handling
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Secrets handling"
description: "The ElevenLabs key and Google client credentials and tokens are stored in the config and masked in logs."
domain: architecture
tags:
  - crosscutting
  - secrets
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/config.rs
  - resource: src-tauri/src/elevenlabs.rs
  - resource: src/routes/settings/+page.svelte
  - resource: vite.config.ts
  - resource: src-tauri/src/google_drive.rs
relations:
  relates_to:
    - crosscutting/configuration
    - building-blocks/rust-elevenlabs
    - runtime/drive-connect-flow
---
# Secrets handling

Secret values travel inside `AppConfig` and are never read from environment variables in the cited sources.

## Facts

- Fields: `elevenlabs_api_key`, `google_drive.client_id`, `client_secret`, `access_token`, `refresh_token` (src-tauri/src/config.rs).
- The key is sent as header `xi-api-key` (src-tauri/src/elevenlabs.rs).
- `test_api_key` logs the first six and last four characters of the key; the settings page builds a similar masked string for `logger.elevenLabsTest` (src/routes/settings/+page.svelte).
- The key field has an `apiKeyVisible` toggle (src/routes/settings/+page.svelte).
- `sync_to_static` comments say the static file is gitignored; `stripConfigPlugin` deletes `build/_config.json` "so API keys don't get bundled" (src-tauri/src/config.rs, vite.config.ts).
- OAuth uses PKCE: `generate_code_verifier` and `code_challenge` (src-tauri/src/google_drive.rs).
- `google_drive_disconnect` does nothing in Rust; the settings page clears tokens in `disconnectDrive`.

## Related

[[crosscutting/configuration]], [[building-blocks/rust-elevenlabs]], [[runtime/drive-connect-flow]]
