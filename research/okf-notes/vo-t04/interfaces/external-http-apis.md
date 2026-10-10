---
id: interfaces/external-http-apis
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "External HTTP calls"
description: "The code calls ElevenLabs and Google endpoints from Rust and, in browser mode, from the page."
domain: architecture
tags:
  - interface
  - http
  - external
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/elevenlabs.rs
  - resource: src-tauri/src/google_drive.rs
  - resource: src/routes/preview/+page.svelte
  - resource: src/routes/settings/+page.svelte
  - resource: src-tauri/tauri.conf.json
relations:
  relates_to:
    - context/system-context
    - building-blocks/rust-elevenlabs
    - building-blocks/rust-google-drive
---
# External HTTP calls

Each row names the endpoint, the call site and the matching browser-mode call.

| Endpoint | Rust call | Browser call |
|---|---|---|
| `GET https://api.elevenlabs.io/v1/user` (header `xi-api-key`) | `test_api_key` in elevenlabs.rs | `testApiKey` in settings/+page.svelte |
| `POST https://api.elevenlabs.io/v1/speech-to-speech/<voice>?output_format=mp3_44100_128` | `speech_to_speech` in elevenlabs.rs | `processViaBrowser` in preview/+page.svelte |
| `GET https://accounts.google.com/o/oauth2/v2/auth` | opened with `open::that` in google_drive.rs | none |
| `POST https://oauth2.googleapis.com/token` (authorization code) | `google_drive_connect` | none |
| `POST https://oauth2.googleapis.com/token` (refresh token) | `refresh_access_token` (unused) | `refreshDriveToken` |
| `GET https://www.googleapis.com/oauth2/v2/userinfo` | `get_user_email` | none |
| `POST https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart` | `upload_to_drive` | `driveUploadWithToken` |
| `POST https://www.googleapis.com/drive/v3/files/<id>/permissions` | `upload_to_drive` | `driveUploadWithToken` |

The `connect-src` directive in src-tauri/tauri.conf.json lists `api.elevenlabs.io`, `oauth2.googleapis.com`, `www.googleapis.com`, `accounts.google.com` and `cdn.jsdelivr.net`.

## Related

[[context/system-context]], [[building-blocks/rust-elevenlabs]], [[building-blocks/rust-google-drive]]
