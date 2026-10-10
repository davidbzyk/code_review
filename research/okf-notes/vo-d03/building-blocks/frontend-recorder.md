---
id: building-blocks/frontend-recorder
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Frontend recorder module"
description: "MediaRecorder wrapper that captures the screen and microphone and returns a file path or blob URL."
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
relations:
  relates_to:
    - runtime/record-screen
    - building-blocks/backend-recording
---

# Frontend recorder module

`src/lib/recorder.svelte.ts` starts, pauses, stops and cancels a recording using browser media APIs.

## Public functions

- `startRecording(captureMode, audioDeviceId?, webcamEnabled?)`: creates a session id `rec-<time>-<random>`, calls `getDisplayMedia` (30 fps ideal, no audio) and `getUserMedia` for the microphone, merges both into one `MediaStream`, and starts a `MediaRecorder` with 1000 ms slices at 2,500,000 bits per second. Prefers `video/webm;codecs=vp8,opus`. Returns a webcam stream (160x120) when `webcamEnabled`, else `null`.
- `pauseRecording()`, `resumeRecording()`.
- `stopRecording(): Promise<string>`: in Tauri calls `finalize_recording` and resolves the file path; in browser mode builds blobs, stores them as `window.__voiceover_blob` and `window.__voiceover_audio_blob`, and resolves an object URL.
- `cancelRecording()`: clears chunks and stops tracks.
- `getAudioDevices()`: lists `audioinput` devices.
- Type `CaptureMode`: `fullscreen`, `window`, `region`; the value is passed to `logger.recordingStart`.

## Chunk handling

Each `ondataavailable` event either invokes `save_recording_chunk` (Tauri) or pushes to `recordedChunks` (browser). In browser mode a second `MediaRecorder` records an audio-only track into `audioChunks`.

## Calls

`logger` (`src/lib/logger.ts`), `isTauri` (`src/lib/state.svelte.ts`), Rust commands in [backend-recording](./backend-recording.md).

## Related

- [runtime/record-screen](../runtime/record-screen.md)
- [building-blocks/page-record](./page-record.md)
- [building-blocks/backend-recording](./backend-recording.md)
- [building-blocks/frontend-logger](./frontend-logger.md)
