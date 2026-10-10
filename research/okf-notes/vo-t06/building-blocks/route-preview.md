---
id: building-blocks/route-preview
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Preview Route"
description: "The page at /preview that plays the recording, processes it and uploads the result."
domain: architecture
tags:
  - building-blocks
  - frontend
  - route
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/preview/+page.svelte
relations:
  relates_to:
    - runtime/process-recording-browser
    - runtime/drive-upload
    - building-blocks/frontend-state
    - runtime/process-recording-tauri
---

`src/routes/preview/+page.svelte` loads the recording for playback and runs the desktop or browser processing path.

## Facts

- On mount: a `blob:` recording path is used directly; in Tauri the file is read with `read_file_bytes` and turned into an object URL.
- `processAndSave()` sets progress state and calls `processViaTauri()` when `isTauri()`, otherwise `processViaBrowser()`.
- `processViaTauri()` invokes `process_recording` with a `Channel` for progress events.
- `processViaBrowser()` either downloads the raw WebM, or posts audio to ElevenLabs and splices with `@ffmpeg/ffmpeg`; see [Process recording, browser](../runtime/process-recording-browser.md).
- `extractAudioFromBlob` decodes with `AudioContext`, rejects clips over 300 seconds, resamples to 16 kHz mono and calls `encodeWav`.
- `downloadBlob(blob, filename)` clicks a temporary link.
- `uploadToDrive()` refreshes an expired token and uploads; see [Drive upload flow](../runtime/drive-upload.md).
- `discard()` and `newRecording()` call `appState.reset()` and `goto('/')`.
- Imports: `appState`, `logger`, `blobStore`, `refreshDriveToken`, `driveUploadWithToken`, `DriveUploadError`.

## Related

- [Frontend state](frontend-state.md)
- [Process recording, desktop](../runtime/process-recording-tauri.md)
