---
id: interfaces/external-http-apis
schema: okf/schemas/v1/architecture.json
type: Architecture
title: External HTTP APIs
description: The third-party URLs the code calls, with the files that call them.
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
  - resource: src/lib/drive.ts
  - resource: src/routes/preview/+page.svelte
  - resource: src/routes/settings/+page.svelte
  - resource: src-tauri/tauri.conf.json
related:
  - context/system-context
  - building-blocks/rust-tts-providers
  - building-blocks/rust-google-drive
---

# External HTTP APIs

| Method and URL | Purpose | Caller |
|---|---|---|
| POST `https://api.elevenlabs.io/v1/speech-to-speech/{voice_id}?output_format=mp3_44100_128` | voice conversion | src-tauri/src/elevenlabs.rs; src/routes/preview/+page.svelte |
| GET `https://api.elevenlabs.io/v1/user` | key test | src-tauri/src/elevenlabs.rs; src/routes/settings/+page.svelte |
| GET `https://accounts.google.com/o/oauth2/v2/auth` | consent page | src-tauri/src/google_drive.rs |
| POST `https://oauth2.googleapis.com/token` | code exchange and refresh | google_drive.rs; src/lib/drive.ts |
| GET `https://www.googleapis.com/oauth2/v2/userinfo` | account email | src-tauri/src/google_drive.rs |
| POST `https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&fields=id,webViewLink` | upload | google_drive.rs; src/lib/drive.ts |

- ElevenLabs form fields: `audio`, `model_id`, `remove_background_noise`; header `xi-api-key`.
- Drive requests use `Authorization: Bearer <token>`.
- The `connect-src` list in the CSP names `api.elevenlabs.io`, `oauth2.googleapis.com`, `www.googleapis.com`, `accounts.google.com` (src-tauri/tauri.conf.json).

## Related

- [System Context](../context/system-context.md)
- [Rust TTS Providers and Models](../building-blocks/rust-tts-providers.md)
- [Rust Google Drive](../building-blocks/rust-google-drive.md)
