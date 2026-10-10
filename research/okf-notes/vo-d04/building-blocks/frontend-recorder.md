---
id: building-blocks/frontend-recorder
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Frontend recorder module"
description: "Browser media capture with MediaRecorder, in chunked Tauri mode or in-memory browser mode."
domain: architecture
tags:
  - frontend
  - recording
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
architecture_layer: building-blocks
sources:
  - resource: src/lib/recorder.svelte.ts
related:
  - runtime/record-screen-flow
  - building-blocks/backend-recording-commands
  - building-blocks/route-home
---

# Frontend recorder module

`src/lib/recorder.svelte.ts` starts, pauses, stops and cancels a screen plus microphone recording.

## Public functions (src/lib/recorder.svelte.ts)
- `startRecording(captureMode, audioDeviceId?, webcamEnabled?)`: calls `getDisplayMedia` (video, 30 fps ideal, no audio) and `getUserMedia` (audio), merges the tracks into one `MediaStream`, creates a `MediaRecorder` at 2,500,000 video bits per second and starts it with a 1000 ms timeslice. Returns a webcam stream when `webcamEnabled`, else null.
- `pauseRecording()`, `resumeRecording()`.
- `stopRecording()`: resolves with a file path (Tauri) or a blob URL (browser).
- `cancelRecording()`.
- `getAudioDevices()`: lists `audioinput` devices.
- Type `CaptureMode`: `fullscreen`, `window`, `region`.

## Mode split
- Tauri: each chunk goes to `save_recording_chunk`; stop calls `finalize_recording`.
- Browser: chunks stay in `recordedChunks`; a second `MediaRecorder` collects audio-only chunks in `audioChunks`; results are placed on `window.__voiceover_blob` and `window.__voiceover_audio_blob`.

## Uses
`logger`, `isTauri` from `./state.svelte`, `@tauri-apps/api/core` `invoke`.

## Related

- [[runtime/record-screen-flow]]
- [[building-blocks/backend-recording-commands]]
- [[building-blocks/route-home]]
