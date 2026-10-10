---
id: interfaces/external-http-apis
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "External HTTP APIs"
description: "The remote endpoints the code calls, with the file that calls each."
domain: architecture
tags:
  - interfaces
  - http
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/elevenlabs.rs
  - resource: src-tauri/src/local_tts.rs
  - resource: src-tauri/src/google_drive.rs
  - resource: src/lib/drive.ts
  - resource: src/lib/voicebox.ts
  - resource: src/routes/preview/+page.svelte
related:
  - building-blocks/backend-tts-providers
  - context/system-context
  - runtime/google-drive-connect
---
# External HTTP APIs

Three remote services are called over HTTP.

## ElevenLabs (src-tauri/src/elevenlabs.rs)
- POST `/v1/speech-to-speech/{voice}?output_format=mp3_44100_128`, multipart `audio`, `model_id`, `remove_background_noise`, header `xi-api-key`; writes the MP3 response.
- GET `/v1/user` for key validation.
- The browser path posts to the same S2S URL (src/routes/preview/+page.svelte).

## Voicebox (src-tauri/src/local_tts.rs, src/lib/voicebox.ts)
- POST `/transcribe` (multipart `file`) returns `text` and `duration`.
- POST `/generate` with `profile_id`, `text`, `engine: "qwen"` returns `id`.
- GET `/generate/{id}/status`; the Rust poller reads the last `data:` line.
- GET `/audio/{id}` returns the audio file.
- GET `/health`, `/profiles`, `/models/status`; POST `/models/load`, `/profiles`, `/profiles/{id}/samples`.

## Google (src-tauri/src/google_drive.rs, src/lib/drive.ts)
- Consent at `accounts.google.com/o/oauth2/v2/auth`.
- POST `oauth2.googleapis.com/token` (code exchange and refresh).
- GET `www.googleapis.com/oauth2/v2/userinfo`.
- POST `www.googleapis.com/upload/drive/v3/files?uploadType=multipart`.

## Related
- [Backend TTS Providers](../building-blocks/backend-tts-providers.md)
- [System Context](../context/system-context.md)
- [Google Drive Connect](../runtime/google-drive-connect.md)
