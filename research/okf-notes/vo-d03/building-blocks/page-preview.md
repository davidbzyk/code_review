---
id: building-blocks/page-preview
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Preview page"
description: "Route /preview that plays the recording, runs processing and uploads the result to Google Drive."
domain: architecture
tags:
  - building-block
  - frontend
  - route
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/preview/+page.svelte
relations:
  relates_to:
    - runtime/process-recording-desktop
    - runtime/process-recording-browser
    - runtime/upload-to-drive
---

# Preview page

`src/routes/preview/+page.svelte` shows the recording and holds both the Tauri and the browser processing paths.

## Functions

- `onMount`: uses a `blob:` recording path directly; in Tauri invokes `read_file_bytes` and builds an object URL of type `video/webm`.
- `processAndSave()`: sets progress state, then calls `processViaTauri()` or `processViaBrowser()`; errors go to `processingError`.
- `processViaTauri()`: opens a `Channel`, invokes `process_recording`, updates `appState` from `progress`, `complete` and `error` events.
- `processViaBrowser()`: S2S request with `fetch`, then ffmpeg.wasm splice (see [process-recording-browser](../runtime/process-recording-browser.md)).
- `extractAudioFromBlob(videoBlob)`: decodes with `AudioContext`, resamples to 16 kHz mono through `OfflineAudioContext`, rejects over 300 seconds.
- `encodeWav(samples, sampleRate)`: writes a 16-bit PCM WAV header and data.
- `downloadBlob(blob, filename)`: anchor download.
- `refreshDriveToken()`, `driveUploadWithToken(blob, accessToken)`: browser-mode Drive calls.
- `uploadToDrive()`: Tauri path invokes `upload_to_drive`; browser path uploads the blob and retries once after HTTP 401.
- `discard()` and `newRecording()`: `appState.reset()` then `goto('/')`.

## Calls

Rust commands `read_file_bytes`, `process_recording`, `upload_to_drive`; `logger`; `appState`.

## Related

- [runtime/process-recording-desktop](../runtime/process-recording-desktop.md)
- [runtime/process-recording-browser](../runtime/process-recording-browser.md)
- [runtime/upload-to-drive](../runtime/upload-to-drive.md)
- [building-blocks/page-record](./page-record.md)
