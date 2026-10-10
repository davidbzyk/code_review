---
id: interfaces/external-http-endpoints
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "External HTTP endpoints"
description: "Third-party URLs the code calls, with the file that calls each."
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
  - interfaces/tauri-commands
---
# External HTTP endpoints

The Tauri content security policy lists the allowed `connect-src` hosts: `api.elevenlabs.io`, `oauth2.googleapis.com`, `www.googleapis.com`, `accounts.google.com` (src-tauri/tauri.conf.json).

| Endpoint | Method | Caller |
|---|---|---|
| `https://api.elevenlabs.io/v1/speech-to-speech/{voice_id}?output_format=mp3_44100_128` | POST multipart `audio`, `model_id`, `remove_background_noise` | elevenlabs.rs `speech_to_speech`; preview page in browser mode |
| `https://api.elevenlabs.io/v1/user` | GET with `xi-api-key` | elevenlabs.rs `test_api_key`; settings page in browser mode |
| `https://accounts.google.com/o/oauth2/v2/auth` | browser redirect | google_drive.rs `google_drive_connect` |
| `https://oauth2.googleapis.com/token` | POST form | google_drive.rs; src/lib/drive.ts `refreshDriveToken` |
| `https://www.googleapis.com/oauth2/v2/userinfo` | GET | google_drive.rs `get_user_email` |
| `https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart` | POST | google_drive.rs `upload_to_drive`; src/lib/drive.ts |

The settings page invokes `test_api_key` in Tauri and fetches directly otherwise.

## Related

- [[context/system-context]]
- [[interfaces/tauri-commands]]
