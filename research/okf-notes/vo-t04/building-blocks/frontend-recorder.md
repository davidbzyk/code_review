---
id: building-blocks/frontend-recorder
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Frontend recorder module"
description: "recorder.svelte.ts wraps MediaRecorder and getDisplayMedia and saves chunks to Rust in Tauri or keeps them in memory in a browser."
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
    - runtime/record-screen-flow
    - interfaces/tauri-commands
    - building-blocks/frontend-pages
---
# Frontend recorder module

The recorder module captures screen and microphone and produces a video file path or blob URL (src/lib/recorder.svelte.ts).

## Exports

- `generateSessionId()`: returns `rec-<Date.now()>-<six random base36 chars>`.
- `selectVideoMimeType()`: prefers `video/webm;codecs=vp8,opus`, then `video/webm`, else an empty string.
- `startRecording(captureMode, audioDeviceId?, webcamEnabled?)`, `pauseRecording()`, `resumeRecording()`, `stopRecording()`, `cancelRecording()`, `getAudioDevices()`.
- Type `CaptureMode`: `fullscreen`, `window`, `region`.

## Behaviour

- Screen video comes from `navigator.mediaDevices.getDisplayMedia`; microphone from `getUserMedia`; the two are combined in one `MediaStream` and recorded with `videoBitsPerSecond: 2_500_000` in 1000 ms slices.
- In Tauri each data chunk goes to the `save_recording_chunk` command; `stopRecording()` calls `finalize_recording`.
- In a browser, chunks stay in `recordedChunks`; a second recorder keeps an audio-only track in `audioChunks`. On stop, the blobs are placed on `window.__voiceover_blob` and `window.__voiceover_audio_blob` and a blob URL is returned.
- `webcamEnabled` makes `startRecording` return a 160 by 120 webcam stream from `getWebcamStream()`.

## Uses

`logger`, `isTauri`.

## Related

[[runtime/record-screen-flow]], [[interfaces/tauri-commands]], [[building-blocks/frontend-pages]]
