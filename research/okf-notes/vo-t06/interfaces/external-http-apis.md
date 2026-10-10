---
id: interfaces/external-http-apis
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "External HTTP APIs"
description: "The outside HTTP endpoints the code calls and where."
domain: architecture
tags:
  - interfaces
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
relations:
  relates_to:
    - context/system-context
    - building-blocks/rust-elevenlabs
    - building-blocks/rust-google-drive
---

Calls go either from Rust with `reqwest` or from the webview with `fetch`.

| Endpoint | Method | Purpose | Caller |
|---|---|---|---|
| `https://api.elevenlabs.io/v1/speech-to-speech/{voice}` | POST | voice conversion | `elevenlabs.rs`; `preview/+page.svelte` |
| `https://api.elevenlabs.io/v1/user` | GET | key check | `elevenlabs.rs`; `settings/+page.svelte` |
| `https://accounts.google.com/o/oauth2/v2/auth` | browser open | consent | `google_drive.rs` |
| `https://oauth2.googleapis.com/token` | POST | code exchange, refresh | `google_drive.rs`; `drive.ts` |
| `https://www.googleapis.com/oauth2/v2/userinfo` | GET | email | `google_drive.rs` |
| `https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart` | POST | upload | `google_drive.rs`; `drive.ts` |

The `connect-src` list in the Content Security Policy of `src-tauri/tauri.conf.json` names `https://api.elevenlabs.io`, `https://oauth2.googleapis.com`, `https://www.googleapis.com` and `https://accounts.google.com`.

The webview also fetches `/ffmpeg/ffmpeg-core.js` and `/ffmpeg/ffmpeg-core.wasm` from its own origin, and `/_config.json` (`src/lib/state.svelte.ts`).

## Related

- [System context](../context/system-context.md)
- [Rust ElevenLabs](../building-blocks/rust-elevenlabs.md)
- [Rust Google Drive](../building-blocks/rust-google-drive.md)
