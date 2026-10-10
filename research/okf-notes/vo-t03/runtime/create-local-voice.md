---
id: runtime/create-local-voice
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Create a local voice profile"
description: "The five-step wizard in the create-voice route."
domain: architecture
tags:
  - runtime
  - voice-profile
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/create-voice/+page.svelte
  - resource: src/lib/voicebox.ts
  - resource: src-tauri/src/local_tts.rs
  - resource: src-tauri/src/models.rs
related:
  - building-blocks/frontend-clients
  - runtime/local-voice-generation
  - interfaces/sidecar-http-routes
---
# Create a local voice profile

The wizard builds a sidecar profile and then makes it the active voice.

## Steps

1. On mount `checkPrerequisites` calls `VoiceboxClient.checkHealth` and `getModelStatus`; if every model is downloaded, `step` moves to 2.
2. `downloadModels` calls `VoiceboxClient.downloadModel` for each missing model, then polls `getModelStatus` every 3000 ms for up to 600 attempts.
3. `createProfile` calls `VoiceboxClient.createProfile(name, language)` (POST `/profiles`) and moves to step 3.
4. Sample from YouTube: `extractFromYouTube` invokes `extract_youtube_audio`, then POSTs `/transcribe-path` through `sidecar_fetch` to fill `referenceText`.
5. Sample from a file: `transcribeUploadedFile` uses `sidecar_upload` to `/transcribe`.
6. `uploadSample` posts to `/profiles/<id>/samples/from-path` (YouTube) or calls `VoiceboxClient.uploadSample` (file), then moves to step 4.
7. `testGenerate` calls `testGenerate`, `pollGenerationStatus` and `getAudioUrl`.
8. `finishWizard` sets `local_voice_profile_id` and `provider = 'local'`, calls `saveConfig`, and goes to `/settings`.

## Related

- [[building-blocks/frontend-clients]]
- [[runtime/local-voice-generation]]
- [[interfaces/sidecar-http-routes]]
