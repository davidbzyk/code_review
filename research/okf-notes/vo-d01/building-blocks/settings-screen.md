---
id: building-blocks/settings-screen
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Settings Screen"
description: "The /settings route for the API key, voices, and Google Drive connection."
domain: architecture
tags:
  - building-block
  - svelte
  - route
  - settings
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/settings/+page.svelte
---
# Settings Screen

`src/routes/settings/+page.svelte` edits `appState.config` and saves it.

## Facts
- `testApiKey` masks the key for the log, then invokes `test_api_key` (Tauri) or fetches `https://api.elevenlabs.io/v1/user` (browser).
- `addVoice`, `removeVoice`, `setDefault` edit `config.voices`; the first voice added becomes default and removing the default promotes the first remaining one.
- `connectDrive` invokes `google_drive_connect` with `clientId` and `clientSecret` in Tauri and merges the returned tokens into `config.google_drive`; in a browser it sets an error text instead.
- `disconnectDrive` clears tokens and sets `connected` false.
- `saveAndBack` calls `appState.saveConfig()` and `goto('/')`.

## Related
- [[runtime/connect-google-drive]]
- [[building-blocks/frontend-state]]
- [[crosscutting/secrets-handling]]
