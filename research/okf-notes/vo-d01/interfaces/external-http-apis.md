---
id: interfaces/external-http-apis
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "External HTTP APIs"
description: "The third-party endpoints the code calls, with the files that call them."
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
---
# External HTTP APIs

Calls go to ElevenLabs and Google; the same endpoints appear in Rust and in browser-mode TypeScript.

| Endpoint | Method | Files |
|---|---|---|
| `api.elevenlabs.io/v1/speech-to-speech/{voice}?output_format=mp3_44100_128` | POST multipart | src-tauri/src/elevenlabs.rs, src/routes/preview/+page.svelte |
| `api.elevenlabs.io/v1/user` | GET, header `xi-api-key` | src-tauri/src/elevenlabs.rs, src/routes/settings/+page.svelte |
| `accounts.google.com/o/oauth2/v2/auth` | browser redirect | src-tauri/src/google_drive.rs |
| `oauth2.googleapis.com/token` | POST form | src-tauri/src/google_drive.rs, src/routes/preview/+page.svelte |
| `www.googleapis.com/oauth2/v2/userinfo` | GET bearer | src-tauri/src/google_drive.rs |
| `www.googleapis.com/upload/drive/v3/files?uploadType=multipart` | POST | src-tauri/src/google_drive.rs, src/routes/preview/+page.svelte |
| `www.googleapis.com/drive/v3/files/{id}/permissions` | POST JSON | src-tauri/src/google_drive.rs, src/routes/preview/+page.svelte |

## Related
- [[context/system-context]]
- [[building-blocks/elevenlabs-client]]
- [[building-blocks/google-drive-backend]]
