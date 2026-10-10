---
id: building-blocks/frontend-integrations
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Frontend Integrations
description: Browser-side clients for the sidecar (through Tauri) and for the Google Drive HTTP API.
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
  - interfaces/commands-sidecar-proxy
  - runtime/google-drive-connect-upload
  - runtime/create-voice-profile
  - building-blocks/frontend-state-and-config
---

# Frontend Integrations

`voicebox.ts` wraps the sidecar API; `drive.ts` calls Google endpoints directly with `fetch`.

## voicebox.ts

- `VoiceboxClient` methods: `checkHealth` (`test_local_connection`), `listProfiles` (`list_local_voices`), `getModelStatus` (`check_model_status`), `downloadModel`, `createProfile`, `uploadSample`, `testGenerate`, `pollGenerationStatus`, `getAudioUrl`.
- Private `jsonRequest` calls the `sidecar_fetch` command and parses the JSON text.
- `uploadSample` calls `sidecar_upload` with field name `audio` and path `/profiles/{id}/samples`.
- `pollGenerationStatus` calls `poll_generation` every 2000 ms for up to 300000 ms.
- `getAudioUrl` calls `get_generation_audio` and returns a `blob:` URL.
- Interfaces `VoiceboxProfile`, `VoiceboxModelStatus`, `VoiceboxGeneration`.

## drive.ts

- `refreshDriveToken()` posts to `https://oauth2.googleapis.com/token` with `grant_type: 'refresh_token'`, stores the new token and `expires_at` (minus 60 seconds), and calls `appState.saveConfig()`.
- `driveUploadWithToken(blob, accessToken)` posts multipart to the Drive upload URL and returns `webViewLink`.
- `DriveUploadError` carries the HTTP `status`.

## Used by

`/create-voice` uses `VoiceboxClient`; `/preview` uses the drive functions.

## Related

- [Tauri Commands: Local TTS and Sidecar Proxy](../interfaces/commands-sidecar-proxy.md)
- [Flow: Connect and Upload to Google Drive](../runtime/google-drive-connect-upload.md)
- [Flow: Create a Local Voice Profile](../runtime/create-voice-profile.md)
- [Frontend State and Config](./frontend-state-and-config.md)
