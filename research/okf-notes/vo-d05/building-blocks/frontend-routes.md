---
id: building-blocks/frontend-routes
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Frontend routes
description: The SvelteKit pages: record, preview, settings, create-voice wizard and the recording widget.
domain: architecture
tags:
  - building-block
  - frontend
  - ui
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
  - building-blocks/frontend-recorder
  - building-blocks/frontend-voicebox-client
  - runtime/process-recording-elevenlabs
  - runtime/browser-mode-pipeline
  - runtime/drive-connect-and-upload
---

# Frontend routes

Five pages implement the user-facing screens; navigation uses `goto`.

## Pages

- `/` (`+page.svelte`): capture mode and microphone choice, record, pause, stop, cancel; `handleStop` stores `recordingPath` and navigates to `/preview`. Shows `RegionSelector` and `WebcamBubble`.
- `/preview` (`preview/+page.svelte`): loads the video (`read_file_bytes` in Tauri), `processAndSave` runs `processViaTauri` or `processViaBrowser`, `uploadToDrive`, `discard`, `newRecording`.
- `/settings` (`settings/+page.svelte`): provider switch (`setProvider`), ElevenLabs key test (`testApiKey`), voice list edit (`addVoice`, `removeVoice`, `setDefault`), local voice choice and removal, Drive `connectDrive` and `disconnectDrive`, `saveAndBack`.
- `/create-voice` (`create-voice/+page.svelte`): wizard steps: check models, `downloadModels`, `createProfile`, sample from YouTube (`extractFromYouTube`) or file (`transcribeUploadedFile`), `uploadSample`, `testGenerate`, `finishWizard`.
- `/widget` (`widget/+page.svelte`): small always-on-top window with timer, pause, stop and cancel; it emits `recording-pause`, `recording-resume`, `recording-stop`, `recording-cancel` events and invokes `close_widget_window`; it listens for `widget-voice-name`.

## Uses

- `appState`, `tauriInvoke`, `logger`, `blobStore`, `drive.ts`, `VoiceboxClient` and the Tauri commands in [[interfaces/tauri-commands]].

## Related

- [[building-blocks/frontend-recorder]] - Frontend recorder and overlays
- [[building-blocks/frontend-voicebox-client]] - Voicebox client
- [[runtime/process-recording-elevenlabs]] - Process recording with ElevenLabs
- [[runtime/browser-mode-pipeline]] - Browser mode pipeline
- [[runtime/drive-connect-and-upload]] - Google Drive connect and upload
