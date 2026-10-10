---
id: building-blocks/frontend-clients
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Frontend service clients"
description: "Browser-side helpers for Google Drive uploads and for the local TTS sidecar."
domain: architecture
tags:
  - building-block
  - frontend
  - client
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/lib/drive.ts
  - resource: src/lib/voicebox.ts
related:
  - interfaces/sidecar-http-routes
  - runtime/google-drive-connect-and-upload
  - runtime/create-local-voice
---
# Frontend service clients

Two small modules wrap remote calls so pages do not build requests themselves.

## drive.ts

- `DriveUploadError` extends `Error` and keeps the HTTP `status`.
- `refreshDriveToken()` posts a `refresh_token` grant to `https://oauth2.googleapis.com/token`, writes `access_token` and `expires_at` into `appState.config.google_drive`, and calls `appState.saveConfig()`.
- `driveUploadWithToken(blob, accessToken)` posts a multipart upload to `https://www.googleapis.com/upload/drive/v3/files` with the file name `voiceover-<timestamp>.webm` and returns `webViewLink`.

## voicebox.ts

- `VoiceboxClient` with `checkHealth` (`test_local_connection`), `listProfiles` (`list_local_voices`), `getModelStatus` (`check_model_status`), `downloadModel`, `createProfile`, `uploadSample`, `testGenerate`, `pollGenerationStatus`, `getAudioUrl`.
- `jsonRequest` sends through the Tauri command `sidecar_fetch`; `uploadSample` uses `sidecar_upload`.
- `pollGenerationStatus` polls every 1000 ms with a 300000 ms timeout.
- `getAudioUrl` reads `port` from `get_sidecar_status` and returns `http://127.0.0.1:<port>/audio/<id>`.

## Used by

`drive.ts` is used by src/routes/preview/+page.svelte. `voicebox.ts` is used by src/routes/create-voice/+page.svelte.

## Related

- [[interfaces/sidecar-http-routes]]
- [[runtime/google-drive-connect-and-upload]]
- [[runtime/create-local-voice]]
