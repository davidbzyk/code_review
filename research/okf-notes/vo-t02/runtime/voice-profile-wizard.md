---
id: runtime/voice-profile-wizard
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Voice Profile Wizard"
description: "The five-step flow that creates a local Voicebox voice profile."
domain: architecture
tags:
  - runtime
  - voicebox
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/create-voice/+page.svelte
  - resource: src/lib/voicebox.ts
  - resource: src-tauri/src/local_tts.rs
related:
  - building-blocks/frontend-integrations
  - interfaces/tauri-commands-providers
  - interfaces/external-http-apis
---
# Voice Profile Wizard

The wizard in `/create-voice` drives `VoiceboxClient` and ends by selecting the new profile.

## Steps
1. `checkPrerequisites` calls `checkHealth` and `getModelStatus`; if a model name contains `qwen` and is downloaded it moves to step 2.
2. `downloadQwen` calls `downloadModel`, which posts `/models/load`.
3. `createProfile` calls `createProfile(name, language)`, which posts `/profiles`, and stores `profileId`.
4. `uploadSample` calls `uploadSample`, posting to `/profiles/<id>/samples` with `reference_text`.
5. `testGenerate` calls `testGenerate` (`/generate`, engine `qwen`), then `pollGenerationStatus`, then `getAudioUrl`.
6. `finishWizard` sets `local_voice_profile_id` and `provider = 'local'`, calls `saveConfig`, and goes to `/settings`.

Under Tauri these calls pass through `voicebox_fetch`, `voicebox_upload` and the other Voicebox commands.

## Related
- [Frontend Integrations](../building-blocks/frontend-integrations.md)
- [Tauri Commands: Config, Providers and Drive](../interfaces/tauri-commands-providers.md)
- [External HTTP APIs](../interfaces/external-http-apis.md)
