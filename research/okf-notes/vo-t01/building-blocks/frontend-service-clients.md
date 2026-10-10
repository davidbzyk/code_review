---
id: building-blocks/frontend-service-clients
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Frontend Service Clients
description: TypeScript clients for the local TTS sidecar and Google Drive.
domain: architecture
tags:
  - building-block
  - frontend
  - client
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/lib/voicebox.ts
  - resource: src/lib/drive.ts
  - resource: src/lib/logger.ts
relations:
  relates_to:
    - building-blocks/rust-local-tts-and-sidecar
    - runtime/upload-recording-to-drive
    - runtime/create-voice-profile
    - crosscutting/logging
---
# Frontend Service Clients

Two small modules wrap remote calls so pages do not build requests themselves.

## `voicebox.ts`

`VoiceboxClient` has `checkHealth`, `listProfiles`, `getModelStatus`, `createProfile`, `uploadSample`, `testGenerate`, `pollGenerationStatus`, `getAudioUrl`, `downloadModel`, and a private `jsonRequest`. Each method calls a Tauri command: `test_local_connection`, `list_local_voices`, `check_model_status`, `sidecar_fetch`, `sidecar_upload`, `poll_generation`, `get_generation_audio`, `download_model`. `pollGenerationStatus` waits up to 300000 ms in 2000 ms steps.

## `drive.ts`

- `refreshDriveToken` posts to `https://oauth2.googleapis.com/token` with `grant_type: refresh_token`, stores the new token in `appState.config.google_drive`, and calls `saveConfig`.
- `driveUploadWithToken` posts a multipart form to the Drive upload URL and returns `webViewLink`.
- `DriveUploadError` carries the HTTP `status`.

## `logger.ts`

Console logger, described in [Logging](../crosscutting/logging.md).

## Related

- [Rust Local TTS and Sidecar Manager](rust-local-tts-and-sidecar.md)
- [Flow: Connect and Upload to Google Drive](../runtime/upload-recording-to-drive.md)
- [Flow: Create a Voice Profile](../runtime/create-voice-profile.md)
- [Logging](../crosscutting/logging.md)
