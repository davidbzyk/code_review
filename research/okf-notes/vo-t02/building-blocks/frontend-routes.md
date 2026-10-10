---
id: building-blocks/frontend-routes
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Frontend Routes"
description: "The five pages of the SvelteKit app and what each one does."
domain: architecture
tags:
  - building-block
  - frontend
  - routes
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/+page.svelte
  - resource: src/routes/preview/+page.svelte
  - resource: src/routes/settings/+page.svelte
  - resource: src/routes/create-voice/+page.svelte
  - resource: src/routes/widget/+page.svelte
related:
  - building-blocks/frontend-recording
  - building-blocks/frontend-state
  - building-blocks/frontend-integrations
  - runtime/record-flow
---
# Frontend Routes

The routes are the screens a user moves through: record, preview and save, settings, voice wizard and the recording widget.

## Pages
- `/` (src/routes/+page.svelte): capture mode picker, microphone picker, record, pause, stop, cancel; `handleStop` ends with `goto('/preview')`.
- `/preview` (src/routes/preview/+page.svelte): shows the recording, runs `processAndSave`, offers Google Drive upload with `uploadToDrive`, and `discard` or `newRecording`.
- `/settings` (src/routes/settings/+page.svelte): ElevenLabs key test, voice list, provider switch, local Voicebox connection, Google Drive connect and disconnect.
- `/create-voice` (src/routes/create-voice/+page.svelte): five-step wizard (`step` 1 to 5) that uses `VoiceboxClient`; `finishWizard` stores `local_voice_profile_id`.
- `/widget` (src/routes/widget/+page.svelte): small always-on-top panel with a timer; it emits `recording-stop`, `recording-cancel`, `recording-pause` or `recording-resume` and listens for `widget-voice-name`.

## Uses
- [Frontend Recording](./frontend-recording.md) for capture.
- [Frontend State](./frontend-state.md) for `appState`.
- [Frontend Integrations](./frontend-integrations.md) for Voicebox and Drive helpers.
- Tauri commands from [Tauri Commands: Recording and Pipeline](../interfaces/tauri-commands-recording-and-pipeline.md) and [Tauri Commands: Config, Providers and Drive](../interfaces/tauri-commands-providers.md).

## Related
- [Record Flow](../runtime/record-flow.md)
