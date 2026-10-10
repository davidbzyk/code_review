---
id: building-blocks/frontend-preview-page
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Preview page
description: The /preview route: plays the recording, processes it, and uploads the result to Drive.
domain: architecture
tags:
  - building-block
  - frontend
  - pipeline
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/preview/+page.svelte
related:
  - runtime/process-recording-desktop
  - runtime/process-recording-browser
  - runtime/drive-upload
  - building-blocks/backend-pipeline
---

src/routes/preview/+page.svelte shows a `<video controls>` player for `appState.recordingPath` and runs the processing and upload actions.

## Functions
- `processAndSave()`: sets progress, calls `processViaTauri()` or `processViaBrowser()` depending on `isTauri()`, reports errors to `processingError` and `logger.pipelineError`.
- `processViaTauri()`: creates a `Channel`, invokes `process_recording` with `recordingPath`, `voiceReplacement`, `onEvent`.
- `processViaBrowser()`: sends audio to ElevenLabs with `fetch`, splices with ffmpeg.wasm, downloads a `.webm`.
- `extractAudioFromBlob()`: decodes with `AudioContext`, resamples to 16000 Hz mono with `OfflineAudioContext`, encodes through `encodeWav()`; rejects audio over 300 seconds.
- `downloadBlob()`.
- `refreshDriveToken()`, `driveUploadWithToken()`, `uploadToDrive()`.
- `discard()` and `newRecording()` call `appState.reset()` and `goto('/')`.

## Uses
`appState`, `logger`, `@ffmpeg/ffmpeg`, `@ffmpeg/util`, and the commands `process_recording` and `upload_to_drive`.

## Related
[[runtime/process-recording-desktop]], [[runtime/process-recording-browser]], [[runtime/drive-upload]], [[building-blocks/backend-pipeline]]
