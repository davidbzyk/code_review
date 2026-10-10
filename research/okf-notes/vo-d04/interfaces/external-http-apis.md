---
id: interfaces/external-http-apis
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "External HTTP endpoints"
description: "Each remote URL the code calls, with the calling files."
domain: architecture
tags:
  - interfaces
  - http
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
architecture_layer: interfaces
sources:
  - resource: src-tauri/src/elevenlabs.rs
  - resource: src-tauri/src/google_drive.rs
  - resource: src/routes/preview/+page.svelte
  - resource: src/routes/settings/+page.svelte
  - resource: src-tauri/tauri.conf.json
related:
  - context/system-context
  - crosscutting/secrets
---

# External HTTP endpoints

The app calls ElevenLabs and Google over HTTPS.

| Method and URL | Purpose | Callers |
|---|---|---|
| POST api.elevenlabs.io/v1/speech-to-speech/{voice_id} | voice transform | elevenlabs.rs; preview/+page.svelte |
| GET api.elevenlabs.io/v1/user | key check | elevenlabs.rs; settings/+page.svelte |
| GET accounts.google.com/o/oauth2/v2/auth | consent page (opened in browser) | google_drive.rs |
| POST oauth2.googleapis.com/token | code exchange, refresh | google_drive.rs; preview/+page.svelte |
| GET www.googleapis.com/oauth2/v2/userinfo | account email | google_drive.rs |
| POST www.googleapis.com/upload/drive/v3/files | upload | google_drive.rs; preview/+page.svelte |
| POST www.googleapis.com/drive/v3/files/{id}/permissions | share link | google_drive.rs; preview/+page.svelte |

The same hosts appear in the CSP `connect-src` (src-tauri/tauri.conf.json).

## Related

- [[context/system-context]]
- [[crosscutting/secrets]]
