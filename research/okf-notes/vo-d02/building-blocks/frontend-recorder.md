---
id: building-blocks/frontend-recorder
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Frontend recorder module
description: Browser media capture: screen stream, microphone, MediaRecorder and chunk handling.
domain: architecture
tags:
  - building-block
  - frontend
  - recording
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/lib/recorder.svelte.ts
related:
  - runtime/record-a-session
  - building-blocks/backend-recording-commands
  - building-blocks/frontend-record-page
---

src/lib/recorder.svelte.ts wraps `getDisplayMedia`, `getUserMedia` and `MediaRecorder` behind exported functions.

## Exports
- `startRecording(captureMode, audioDeviceId?, webcamEnabled?)`: returns a `MediaStream` for the webcam when enabled, else null.
- `pauseRecording()`, `resumeRecording()`, `stopRecording()` (resolves with a path or blob URL), `cancelRecording()`, `getAudioDevices()`.
- Type `CaptureMode`: `fullscreen`, `window`, `region`.

## Module state
`mediaRecorder`, `audioRecorder`, `screenStream`, `audioStream`, `chunkIndex`, `sessionId`, and in-memory `recordedChunks` and `audioChunks` for browser mode.

## Behaviour
- Session ids look like `rec-<time>-<random>` (`generateSessionId`).
- Video is captured at ideal 30 fps; MIME `video/webm;codecs=vp8,opus` when supported, at 2,500,000 bits per second; `start(1000)` yields one-second chunks.
- Under Tauri each chunk goes to the command `save_recording_chunk`; `stopRecording` calls `finalize_recording`.
- In a browser, chunks stay in memory; a second audio-only recorder runs; blobs are stored on `window.__voiceover_blob` and `window.__voiceover_audio_blob`.
- `cleanup()` stops all tracks and clears the recorder references.

## Uses
`logger`, `isTauri`; Rust commands in [[building-blocks/backend-recording-commands]].

## Related
[[runtime/record-a-session]], [[building-blocks/frontend-record-page]]
