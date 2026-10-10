---
id: building-blocks/route-preview
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Route /preview"
description: "Preview, process, save and upload of a finished recording."
domain: architecture
tags:
  - frontend
  - route
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
architecture_layer: building-blocks
sources:
  - resource: src/routes/preview/+page.svelte
related:
  - runtime/process-recording-desktop-flow
  - runtime/process-recording-browser-flow
  - runtime/google-drive-upload-flow
  - building-blocks/backend-pipeline
---

# Route /preview

`src/routes/preview/+page.svelte` plays the recording and runs processing and upload.

## Functions (src/routes/preview/+page.svelte)
- `onMount`: uses a `blob:` path directly; in Tauri reads bytes with `read_file_bytes` and makes an object URL.
- `processAndSave()`: runs `processViaTauri()` or `processViaBrowser()`.
- `processViaTauri()`: opens a `Channel`, invokes `process_recording`.
- `processViaBrowser()`: S2S request with `fetch`, then ffmpeg.wasm.
- `extractAudioFromBlob()`, `encodeWav()`, `downloadBlob()`.
- `refreshDriveToken()`, `driveUploadWithToken()`, `uploadToDrive()`.
- `discard()` and `newRecording()` call `appState.reset()` and `goto('/')`.

## Uses
`appState`, `isTauri`, `logger`; commands `read_file_bytes`, `process_recording`, `upload_to_drive`; `@ffmpeg/ffmpeg`, `@ffmpeg/util`; ElevenLabs and Google endpoints.

## Related

- [[runtime/process-recording-desktop-flow]]
- [[runtime/process-recording-browser-flow]]
- [[runtime/google-drive-upload-flow]]
- [[building-blocks/backend-pipeline]]
