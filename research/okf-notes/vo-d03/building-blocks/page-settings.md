---
id: building-blocks/page-settings
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Settings page"
description: "Route /settings for the ElevenLabs key, voice list and Google Drive connection."
domain: architecture
tags:
  - building-block
  - frontend
  - route
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/settings/+page.svelte
relations:
  relates_to:
    - runtime/google-drive-connect
    - crosscutting/secrets
---

# Settings page

`src/routes/settings/+page.svelte` edits `appState.config` and saves it.

## Functions

- `saveAndBack()`: `appState.saveConfig()` then `goto('/')`.
- `testApiKey()`: trims the key, logs a masked form, and in Tauri invokes `test_api_key` with `apiKey`; in browser mode `fetch`es `https://api.elevenlabs.io/v1/user` with header `xi-api-key`. Result goes to `keyValid`, with `testError` set to `HTTP <status>` on a failed response.
- `addVoice()`: appends a `Voice` (`id`, `name`, empty `description`, `is_default` true when it is the first voice).
- `removeVoice(id)`: removes it and makes the first remaining voice the default when the removed one was default.
- `setDefault(id)`: marks one voice default.
- `connectDrive()`: in Tauri invokes `google_drive_connect` with `clientId` and `clientSecret`, merges the returned tokens into `config.google_drive` and saves; in browser mode sets `driveError` saying the desktop app is required.
- `disconnectDrive()`: clears the token and email fields and saves.

## Uses

`appState`, `isTauri`, `logger`; Rust commands [backend-elevenlabs](./backend-elevenlabs.md) and [backend-google-drive](./backend-google-drive.md).

## Related

- [runtime/google-drive-connect](../runtime/google-drive-connect.md)
- [crosscutting/secrets](../crosscutting/secrets.md)
- [building-blocks/frontend-state](./frontend-state.md)
