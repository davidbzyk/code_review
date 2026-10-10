---
id: building-blocks/frontend-integrations
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Frontend Integrations"
description: "Client code for the Voicebox server and Google Drive used by the pages."
domain: architecture
tags:
  - building-block
  - frontend
  - integration
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/lib/voicebox.ts
  - resource: src/lib/drive.ts
related:
  - runtime/voice-profile-wizard
  - runtime/drive-upload
  - interfaces/external-http-apis
---
# Frontend Integrations

Two helper modules wrap remote services for the webview.

## src/lib/voicebox.ts
Class `VoiceboxClient(endpoint)` with `checkHealth`, `listProfiles`, `getModelStatus`, `downloadModel`, `createProfile`, `uploadSample`, `testGenerate`, `pollGenerationStatus` and `getAudioUrl`. Under Tauri it calls `test_local_connection`, `list_local_voices`, `check_model_status`, `voicebox_fetch` and `voicebox_upload`; in a browser it uses `fetch`. Polling uses a 300000 ms timeout and a 1000 ms interval.

## src/lib/drive.ts
- `refreshDriveToken` posts a refresh-token grant to https://oauth2.googleapis.com/token and updates `appState.config.google_drive`.
- `driveUploadWithToken` posts multipart data to the Drive upload URL and returns `webViewLink`.
- `DriveUploadError` carries the HTTP `status`.

## Used by
- src/routes/create-voice/+page.svelte uses `VoiceboxClient`.
- src/routes/preview/+page.svelte uses the Drive functions.

## Related
- [Voice Profile Wizard](../runtime/voice-profile-wizard.md)
- [Drive Upload](../runtime/drive-upload.md)
- [External HTTP APIs](../interfaces/external-http-apis.md)
