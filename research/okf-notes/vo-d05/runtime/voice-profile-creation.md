---
id: runtime/voice-profile-creation
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Create a local voice profile
description: Wizard flow from model download to a profile with a reference sample.
domain: architecture
tags:
  - runtime
  - local-tts
  - ui
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/create-voice/+page.svelte
  - resource: src/lib/voicebox.ts
  - resource: src-tauri/src/local_tts.rs
  - resource: src-tauri/sidecar/profiles.py
related:
  - building-blocks/frontend-voicebox-client
  - building-blocks/sidecar-engine
  - interfaces/sidecar-http-routes
---

# Create a local voice profile

The create-voice page walks through numbered steps using `VoiceboxClient` and sidecar commands.

## Steps

1. `checkPrerequisites` calls `checkHealth` (`test_local_connection`), then `getModelStatus` (`check_model_status`); if every model is downloaded it jumps to step 2.
2. `downloadModels` calls `downloadModel` for each model not downloaded, then polls model status every 3 s (up to 600 tries).
3. `createProfile` calls `VoiceboxClient.createProfile`, which posts `/profiles`; `create_profile` (profiles.py) writes `profile.json`.
4. The sample comes from YouTube: `extractFromYouTube` invokes `extract_youtube_audio`, then posts `/transcribe-path` to fill `referenceText`.
5. Or from a file: `transcribeUploadedFile` uses `sidecar_upload` to `/transcribe`.
6. `uploadSample` stores audio and text: `VoiceboxClient.uploadSample` (`sidecar_upload` to `/profiles/{id}/samples`) for a file, or `sidecar_fetch` to `/profiles/{id}/samples/from-path` for the YouTube clip.
7. `testGenerate` starts `/generate` and `pollGenerationStatus` waits.
8. `finishWizard` navigates to `/settings`.

## Related

- [[building-blocks/frontend-voicebox-client]] - Voicebox client
- [[building-blocks/sidecar-engine]] - Sidecar engine modules
- [[interfaces/sidecar-http-routes]] - Sidecar HTTP routes
