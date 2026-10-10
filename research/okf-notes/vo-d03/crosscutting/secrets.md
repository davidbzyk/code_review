---
id: crosscutting/secrets
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Secrets handling"
description: "Where the ElevenLabs key and Google credentials are held, copied and blanked."
domain: architecture
tags:
  - crosscutting
  - secrets
  - arc42-8
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/config.rs
  - resource: src/lib/state.svelte.ts
  - resource: src/routes/settings/+page.svelte
  - resource: src-tauri/src/elevenlabs.rs
  - resource: .gitignore
relations:
  relates_to:
    - crosscutting/configuration
    - building-blocks/backend-config
---

# Secrets handling

Secrets are fields of `AppConfig`; the code stores them in config files and `localStorage` and blanks them in one export.

## Where they live

- `elevenlabs_api_key`, `google_drive.client_secret`, `access_token`, `refresh_token` in `AppConfig` (`src-tauri/src/config.rs`, `src/lib/state.svelte.ts`).
- Persisted to `config.json` in app data and to `localStorage` key `voiceover-config`.
- The settings page has an `apiKeyVisible` toggle (`src/routes/settings/+page.svelte`).

## Handling in code

- `sync_to_static` writes `static/_config.json` with `elevenlabs_api_key`, `client_id`, `client_secret`, `access_token` and `refresh_token` set to empty strings.
- `read_static_config` can read a user-placed `static/_config.json` that does contain a key.
- `.gitignore` lists `static/_config.json` under "Config with secrets".
- `test_api_key` logs a masked form of the key (`src-tauri/src/elevenlabs.rs`); `testApiKey()` does the same in TypeScript.
- Requests send the key in header `xi-api-key`, and Drive tokens as bearer tokens.

## Related

- [crosscutting/configuration](./configuration.md)
- [building-blocks/backend-config](../building-blocks/backend-config.md)
- [runtime/google-drive-connect](../runtime/google-drive-connect.md)
