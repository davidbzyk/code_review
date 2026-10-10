---
id: building-blocks/route-settings
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Route /settings"
description: "Settings page for the API key, voices, output folder and Google Drive."
domain: architecture
tags:
  - frontend
  - route
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
architecture_layer: building-blocks
sources:
  - resource: src/routes/settings/+page.svelte
related:
  - crosscutting/secrets
  - runtime/google-drive-connect-flow
  - interfaces/tauri-commands
  - building-blocks/frontend-state
---

# Route /settings

`src/routes/settings/+page.svelte` edits `appState.config` fields.

## Functions (src/routes/settings/+page.svelte)
- `saveAndBack()`: `appState.saveConfig()` then `goto('/')`.
- `testApiKey()`: Tauri calls `test_api_key`; browser fetches `https://api.elevenlabs.io/v1/user` with header `xi-api-key`.
- `addVoice()`, `removeVoice(id)`, `setDefault(id)`: edit `config.voices`; the first voice added becomes default.
- `connectDrive()`: Tauri calls `google_drive_connect` with `clientId` and `clientSecret`; browser mode sets a message that the desktop app is required.
- `disconnectDrive()`: clears tokens and email, sets `connected` false, saves.
- Inputs bind to `elevenlabs_api_key`, `output_dir`, `google_drive.client_id`, `google_drive.client_secret`.

## Related

- [[crosscutting/secrets]]
- [[runtime/google-drive-connect-flow]]
- [[interfaces/tauri-commands]]
- [[building-blocks/frontend-state]]
