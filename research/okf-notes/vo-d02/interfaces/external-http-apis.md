---
id: interfaces/external-http-apis
schema: okf/schemas/v1/architecture.json
type: Architecture
title: External HTTP calls
description: Each outbound HTTP request with method, URL and the file that makes it.
domain: architecture
tags:
  - interfaces
  - http
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/elevenlabs.rs
  - resource: src-tauri/src/google_drive.rs
  - resource: src/routes/preview/+page.svelte
  - resource: src/routes/settings/+page.svelte
related:
  - context/system-context
  - building-blocks/backend-elevenlabs
  - building-blocks/backend-drive
---

Requests are made by Rust (`reqwest`) and, in browser mode, by `fetch`.

| Method and URL | Purpose | Files |
|---|---|---|
| POST `https://api.elevenlabs.io/v1/speech-to-speech/{voice_id}?output_format=mp3_44100_128` | voice conversion | src-tauri/src/elevenlabs.rs, src/routes/preview/+page.svelte |
| GET `https://api.elevenlabs.io/v1/user` | key check | src-tauri/src/elevenlabs.rs, src/routes/settings/+page.svelte |
| GET `https://accounts.google.com/o/oauth2/v2/auth` | consent page opened in browser | src-tauri/src/google_drive.rs |
| POST `https://oauth2.googleapis.com/token` | code exchange and refresh | src-tauri/src/google_drive.rs, src/routes/preview/+page.svelte |
| GET `https://www.googleapis.com/oauth2/v2/userinfo` | account email | src-tauri/src/google_drive.rs |
| POST `https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&fields=id,webViewLink` | file upload | src-tauri/src/google_drive.rs, src/routes/preview/+page.svelte |
| POST `https://www.googleapis.com/drive/v3/files/{id}/permissions` | public read permission | src-tauri/src/google_drive.rs, src/routes/preview/+page.svelte |

Auth: `xi-api-key` header for ElevenLabs; bearer token for Drive.

## Related
[[context/system-context]], [[building-blocks/backend-elevenlabs]], [[building-blocks/backend-drive]]
