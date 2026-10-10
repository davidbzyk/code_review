---
id: building-blocks/frontend-recorder
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Frontend Recorder"
description: "Browser media capture, webcam compositing and chunk delivery."
domain: architecture
tags:
  - building-blocks
  - frontend
  - recording
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/lib/recorder.svelte.ts
  - resource: src/lib/WebcamBubble.svelte
relations:
  relates_to:
    - runtime/record-screen
    - building-blocks/rust-recording-commands
    - building-blocks/route-record
    - building-blocks/frontend-state
---

`recorder.svelte.ts` drives `getDisplayMedia`, `getUserMedia` and `MediaRecorder`; `WebcamBubble.svelte` shows a live webcam preview.

## Facts

- Exports of `src/lib/recorder.svelte.ts`: `generateSessionId`, `selectVideoMimeType`, `CaptureMode` (`fullscreen`, `window`, `region`), `startRecording`, `computeWebcamBubbleRect`, `pauseRecording`, `resumeRecording`, `stopRecording`, `cancelRecording`, `getAudioDevices`.
- `generateSessionId()` returns `rec-<Date.now()>-<6 random chars>`.
- `selectVideoMimeType()` prefers `video/webm;codecs=vp8,opus`, then `video/webm`.
- `startRecording` creates a `MediaRecorder` with `videoBitsPerSecond: 2_500_000` and starts it with a 5000 ms timeslice.
- When a webcam stream exists, a hidden canvas compositor draws the screen video and a circular mirrored webcam bubble at up to 30 frames per second, capped at 1920 by 1080 (`startCompositorLoop`).
- `computeWebcamBubbleRect` returns diameter between 100 and 240 pixels (12 percent of width) and a margin of at least 16 pixels.
- `WebcamBubble.svelte` draws `appState.webcamVideoEl` into a 120 pixel canvas at 15 frames per second while the state is `recording` or `paused`; `togglePosition` flips `webcam_position` and calls `appState.saveConfig()`.
- Uses `appState`, `logger`, `blobStore`, `tauriInvoke`.

## Related

- [Record screen flow](../runtime/record-screen.md)
- [Rust recording commands](rust-recording-commands.md)
- [Record route](route-record.md)
