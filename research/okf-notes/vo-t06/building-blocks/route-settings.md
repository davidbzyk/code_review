---
id: building-blocks/route-settings
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Settings Route"
description: "The page at /settings for the API key, voices and Google Drive connection."
domain: architecture
tags:
  - building-blocks
  - frontend
  - route
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/settings/+page.svelte
relations:
  relates_to:
    - interfaces/tauri-commands-services
    - runtime/drive-oauth-connect
    - building-blocks/frontend-state
---

`src/routes/settings/+page.svelte` edits `appState.config` and saves it.

## Facts

- `saveAndBack()` calls `appState.saveConfig()` then `goto('/')`.
- `testApiKey()` trims the key; in Tauri it invokes `test_api_key`, in the browser it fetches `https://api.elevenlabs.io/v1/user` with the `xi-api-key` header; the result sets `keyValid`.
- `addVoice()` appends a `Voice` (the first voice added becomes `is_default`); `removeVoice(id)` reassigns the default to the first voice when the default is removed; `setDefault(id)` flags one voice.
- `connectDrive()` invokes `google_drive_connect` with `clientId` and `clientSecret` in Tauri and merges the returned tokens into `config.google_drive`; in the browser it sets an error telling the user to connect in the desktop app.
- `disconnectDrive()` blanks the tokens and email, sets `connected` false and saves.
- Imports: `appState`, `isTauri`, `Voice`, `logger`.

## Related

- [Tauri commands, services](../interfaces/tauri-commands-services.md)
- [Drive OAuth flow](../runtime/drive-oauth-connect.md)
- [Frontend state](frontend-state.md)
