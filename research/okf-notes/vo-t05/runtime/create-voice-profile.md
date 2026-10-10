---
id: runtime/create-voice-profile
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Flow: Create a Local Voice Profile
description: The /create-voice wizard from health check to a saved profile id.
domain: architecture
tags:
  - runtime
  - local-tts
  - frontend
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/create-voice/+page.svelte
  - resource: src/lib/voicebox.ts
  - resource: src-tauri/src/local_tts.rs
  - resource: src-tauri/sidecar/server.py
  - resource: src-tauri/sidecar/profiles.py
related:
  - building-blocks/frontend-integrations
  - interfaces/sidecar-http-profiles-models
  - building-blocks/sidecar-engine
  - runtime/config-load-save
---

# Flow: Create a Local Voice Profile

Trigger: the user opens `/create-voice` from settings.

1. `checkPrerequisites` calls `client.checkHealth` and `client.getModelStatus` (src/routes/create-voice/+page.svelte).
2. `downloadModels` calls `client.downloadModel` per missing model, then polls `getModelStatus` every 3000 ms up to 600 times.
3. `createProfile` calls `client.createProfile(name, language)`, which posts `/profiles` through `sidecar_fetch`; `create_profile` (profiles.py) writes `profile.json`.
4. Sample source is a YouTube clip or a file. YouTube: `extract_youtube_audio` calls `/extract-youtube`; then `sidecar_fetch` posts `/transcribe-path`. File: `sidecar_upload` posts `/transcribe`.
5. `uploadSample` posts `/profiles/{id}/samples/from-path` or calls `client.uploadSample`, which ends in `add_sample`.
6. `testGenerate` posts `/generate`, `pollGenerationStatus` polls, and `getAudioUrl` fetches the WAV for playback.
7. `finishWizard` sets `local_voice_profile_id` and `provider = 'local'`, calls `appState.saveConfig()`, and goes to `/settings`.

## Related

- [Frontend Integrations](../building-blocks/frontend-integrations.md)
- [Sidecar HTTP: Profiles and Models](../interfaces/sidecar-http-profiles-models.md)
- [Sidecar Engine Modules](../building-blocks/sidecar-engine.md)
- [Flow: Load and Save Config](./config-load-save.md)
