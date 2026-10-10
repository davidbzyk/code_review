---
id: building-blocks/frontend-state
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Frontend state and Drive client
description: Reactive application state with config loading and saving, plus a browser-side Google Drive client.
domain: architecture
tags:
  - building-block
  - frontend
  - state
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/lib/state.svelte.ts
  - resource: src/lib/drive.ts
related:
  - building-blocks/tauri-config-secrets
  - crosscutting/state
  - runtime/drive-connect-and-upload
---

# Frontend state and Drive client

`appState` is the single reactive store for configuration and recording progress, and `drive.ts` talks to Google Drive from the browser.

## state.svelte.ts

- Exports `isTauri()` (checks `window.__TAURI_INTERNALS__`), the types `Voice`, `GoogleDrive`, `AppConfig`, `RecordingState`, and the singleton `appState`.
- `RecordingState` values: `ready`, `selecting`, `selecting-region`, `recording`, `paused`, `recorded`, `processing`, `complete`, `saved`.
- `appState` fields include `config`, `webcamStream`, `webcamVideoEl`, `regionScreenshot`, `recordingPath`, `outputPath`, `processingProgress`, `processingStage`, `errorMessage`, `ffmpegAvailable`; derived values `selectedVoice` and `isConfigured`.
- `loadConfig()` order: Tauri `get_config` (when it has an ElevenLabs key), then `/_config.json`, then `localStorage` key `voiceover-config`.
- `saveConfig()` writes sanitized config to `localStorage` and the full config to Tauri `save_config`.
- `sanitizeForStorage` blanks the API key, client secret and tokens before `localStorage`.
- `reset()` stops webcam tracks and clears recording fields.

## drive.ts

- `refreshDriveToken()` posts a refresh-token grant to `https://oauth2.googleapis.com/token` and saves the new token through `appState.saveConfig()`.
- `driveUploadWithToken(blob, accessToken)` posts a multipart upload to the Drive v3 files endpoint and returns `webViewLink`.
- `DriveUploadError` carries the HTTP `status`.

## Uses

- Calls the Rust config commands ([[building-blocks/tauri-config-secrets]]); state handling is described in [[crosscutting/state]].

## Related

- [[building-blocks/tauri-config-secrets]] - Rust config and secrets
- [[crosscutting/state]] - State and storage
- [[runtime/drive-connect-and-upload]] - Google Drive connect and upload
