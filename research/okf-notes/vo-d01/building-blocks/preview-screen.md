---
id: building-blocks/preview-screen
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Preview Screen"
description: "The /preview route that processes the recording, shows progress and uploads to Drive."
domain: architecture
tags:
  - building-block
  - svelte
  - route
  - pipeline
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/preview/+page.svelte
---
# Preview Screen

`src/routes/preview/+page.svelte` runs processing in either runtime and handles upload and reset.

## Facts
- `processAndSave` selects `processViaTauri` or `processViaBrowser`.
- `processViaTauri` invokes `process_recording` with a `Channel` and updates `appState` from `progress`, `complete` and `error` messages.
- `processViaBrowser` posts audio to ElevenLabs with `fetch` and splices with ffmpeg.wasm.
- `extractAudioFromBlob`, `encodeWav`, `downloadBlob` are helpers; `refreshDriveToken`, `driveUploadWithToken`, `uploadToDrive` handle Drive.
- `discard` and `newRecording` call `appState.reset()` and `goto('/')`.

## Calls
`process_recording`, `upload_to_drive`, `@ffmpeg/ffmpeg`, `@ffmpeg/util`, `logger`.

## Related
- [[runtime/process-recording-desktop]]
- [[runtime/process-recording-browser]]
- [[runtime/upload-to-drive]]
- [[building-blocks/frontend-state]]
