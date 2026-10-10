---
id: runtime/create-voice-profile
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Flow: Create a Voice Profile
description: The create-voice wizard from model download to test generation.
domain: architecture
tags:
  - runtime
  - flow
  - profiles
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/(app)/create-voice/+page.svelte
  - resource: src/lib/voicebox.ts
  - resource: src-tauri/src/local_tts.rs
  - resource: src-tauri/src/models.rs
  - resource: src-tauri/sidecar/server.py
  - resource: src-tauri/sidecar/profiles.py
relations:
  relates_to:
    - building-blocks/frontend-service-clients
    - building-blocks/sidecar-engine
    - interfaces/sidecar-http-api
---
# Flow: Create a Voice Profile

This flow creates a local voice profile with one reference sample.

1. `checkPrerequisites` in `src/routes/(app)/create-voice/+page.svelte` calls `VoiceboxClient.checkHealth` and `getModelStatus`.
2. `downloadModels` calls `VoiceboxClient.downloadModel`, which invokes `download_model` (`src-tauri/src/models.rs`) with a `Channel`.
3. `download_model` posts to `/models/download` and forwards each `data:` line as a `ModelDownloadEvent`.
4. `createProfile` calls `VoiceboxClient.createProfile`, which sends `POST /profiles` through `sidecar_fetch`; `profiles.create_profile` writes `profile.json`.
5. `extractFromYouTube` invokes `extract_youtube_audio`; the sidecar route `/extract-youtube` downloads with yt-dlp and cuts a 16 kHz mono WAV with ffmpeg.
6. `transcribeUploadedFile` uses `sidecar_upload` to `/transcribe`; for YouTube audio it posts `/transcribe-path` through `sidecar_fetch`.
7. `uploadSample` posts to `/profiles/{id}/samples/from-path` for YouTube audio, or calls `VoiceboxClient.uploadSample` (`sidecar_upload`) for a file; `profiles.add_sample` writes `<id>.wav` and `<id>.txt`.
8. `testGenerate` posts `/generate`, then `pollGenerationStatus` and `getAudioUrl`.
9. `finishWizard` returns to `/settings`.

## Related

- [Frontend Service Clients](../building-blocks/frontend-service-clients.md)
- [Sidecar Engine Modules](../building-blocks/sidecar-engine.md)
- [Sidecar HTTP API](../interfaces/sidecar-http-api.md)
