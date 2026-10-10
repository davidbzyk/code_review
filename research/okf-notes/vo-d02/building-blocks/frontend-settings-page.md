---
id: building-blocks/frontend-settings-page
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Settings page
description: The /settings route: API key, voice list, output folder and Google Drive connection.
domain: architecture
tags:
  - building-block
  - frontend
  - settings
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/settings/+page.svelte
related:
  - runtime/config-load-and-save
  - runtime/drive-connect
  - building-blocks/backend-elevenlabs
  - building-blocks/backend-drive
---

src/routes/settings/+page.svelte edits `appState.config` and saves it.

## Functions
- `saveAndBack()`: `appState.saveConfig()` then `goto('/')`.
- `testApiKey()`: trims the key, logs a masked form (first 6 and last 4 characters), then invokes `test_api_key` under Tauri or `fetch`es `https://api.elevenlabs.io/v1/user` in a browser; sets `keyValid` and `testError`.
- `addVoice()`: appends a `Voice` (the first one added becomes `is_default`).
- `removeVoice(id)`: removes a voice and makes the first remaining voice default when the default was removed.
- `setDefault(id)`.
- `connectDrive()`: under Tauri invokes `google_drive_connect` with `clientId` and `clientSecret`, merges the returned tokens into `config.google_drive`, saves; in a browser sets a message that the desktop app is required.
- `disconnectDrive()`: clears tokens and email, sets `connected` false, saves.

## Page fields
API key input (type password with a visibility toggle), voice name and id inputs, output directory input, Drive client id and client secret inputs.

## Related
[[runtime/config-load-and-save]], [[runtime/drive-connect]], [[building-blocks/backend-elevenlabs]], [[building-blocks/backend-drive]]
