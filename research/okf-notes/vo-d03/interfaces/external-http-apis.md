---
id: interfaces/external-http-apis
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "External HTTP calls"
description: "Every outbound HTTP endpoint the code uses, with method, caller and file."
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
    - building-blocks/backend-elevenlabs
    - building-blocks/backend-google-drive
---

# External HTTP calls

The app calls three vendors: ElevenLabs, Google OAuth and Google Drive.

| Method and URL | Purpose | Rust caller | TypeScript caller |
|---|---|---|---|
| `POST api.elevenlabs.io/v1/speech-to-speech/{voice}?output_format=mp3_44100_128` | voice conversion | `speech_to_speech` | `processViaBrowser` |
| `GET api.elevenlabs.io/v1/user` | key test | `test_api_key` | `testApiKey` |
| `GET accounts.google.com/o/oauth2/v2/auth` | consent page (opened in browser) | `google_drive_connect` | none |
| `POST oauth2.googleapis.com/token` | code exchange, refresh | `google_drive_connect`, `refresh_access_token` | `refreshDriveToken` |
| `GET www.googleapis.com/oauth2/v2/userinfo` | email | `get_user_email` | none |
| `POST www.googleapis.com/upload/drive/v3/files?uploadType=multipart` | upload | `upload_to_drive` | `driveUploadWithToken` |
| `POST www.googleapis.com/drive/v3/files/{id}/permissions` | public read link | `upload_to_drive` | `driveUploadWithToken` |

Auth: `xi-api-key` header for ElevenLabs; bearer token for Drive. Hosts allowed in the webview are in `connect-src` of `src-tauri/tauri.conf.json`.

Rust code builds clients with `reqwest::Client::new()`.

## Related

- [context/system-context](../context/system-context.md)
- [building-blocks/backend-elevenlabs](../building-blocks/backend-elevenlabs.md)
- [building-blocks/backend-google-drive](../building-blocks/backend-google-drive.md)
- [crosscutting/permissions-and-csp](../crosscutting/permissions-and-csp.md)
