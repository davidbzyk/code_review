---
id: building-blocks/frontend-voicebox-client
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Voicebox client
description: VoiceboxClient is the frontend wrapper that reaches the local TTS sidecar through Tauri commands.
domain: architecture
tags:
  - building-block
  - frontend
  - local-tts
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/lib/voicebox.ts
related:
  - building-blocks/tauri-local-tts-bridge
  - interfaces/tauri-commands
  - runtime/voice-profile-creation
---

# Voicebox client

`src/lib/voicebox.ts` exports the class `VoiceboxClient` and the interfaces `VoiceboxProfile`, `VoiceboxModelStatus`, `VoiceboxGeneration`.

## Methods

- `checkHealth()` calls `test_local_connection`.
- `listProfiles()` calls `list_local_voices`; `getModelStatus()` calls `check_model_status`.
- `downloadModel(modelName)` posts `/models/download` with `{ model_name }` through `sidecar_fetch`.
- `createProfile(name, language)` posts `/profiles` through `sidecar_fetch`.
- `uploadSample(profileId, audioFile, referenceText)` calls `sidecar_upload` with field name `audio` and path `/profiles/{id}/samples`.
- `testGenerate(profileId, text)` posts `/generate` with language `en`.
- `pollGenerationStatus(generationId)` calls `poll_generation` every 2000 ms for up to 300000 ms and returns `completed` or throws on `error`.
- `getAudioUrl(generationId)` reads the port from `get_sidecar_status` and returns `http://127.0.0.1:{port}/audio/{id}`.

## Uses

- Every call goes through `tauriInvoke` ([[building-blocks/tauri-local-tts-bridge]]). The wizard that uses it is in [[building-blocks/frontend-routes]].

## Related

- [[building-blocks/tauri-local-tts-bridge]] - Rust local TTS bridge
- [[interfaces/tauri-commands]] - Tauri commands
- [[runtime/voice-profile-creation]] - Create a local voice profile
