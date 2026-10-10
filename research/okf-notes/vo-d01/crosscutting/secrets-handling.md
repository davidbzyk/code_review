---
id: crosscutting/secrets-handling
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Secrets Handling"
description: "Where the API key and Google credentials are held and how they are masked."
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
  - resource: .gitignore
---
# Secrets Handling

Secrets are fields of `AppConfig`, stored in plain JSON.

## Facts
- `elevenlabs_api_key` and the `GoogleDrive` fields `client_id`, `client_secret`, `access_token`, `refresh_token` are stored in `config.json` (src-tauri/src/config.rs).
- `testApiKey` logs only the first 6 and last 4 characters (src/routes/settings/+page.svelte); `test_api_key` does the same in Rust (src-tauri/src/elevenlabs.rs).
- The settings page has an `apiKeyVisible` toggle.
- `.gitignore` lists `static/_config.json`, the dev-server copy written by `sync_to_static`.
- The browser path also keeps the config in `localStorage` (src/lib/state.svelte.ts).

## Related
- [[crosscutting/configuration]]
- [[building-blocks/elevenlabs-client]]
- [[building-blocks/google-drive-backend]]
