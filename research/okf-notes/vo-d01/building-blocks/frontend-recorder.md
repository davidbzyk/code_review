---
id: building-blocks/frontend-recorder
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Frontend Recorder"
description: "Browser-side capture of screen video and microphone audio with MediaRecorder."
domain: architecture
tags:
  - building-block
  - svelte
  - recording
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/lib/recorder.svelte.ts
---
# Frontend Recorder

`recorder.svelte.ts` starts, pauses, stops and cancels capture and hands chunks to Rust or memory.

## Facts
- `startRecording(captureMode, audioDeviceId?, webcamEnabled?)` calls `getDisplayMedia` (30 fps, no audio) and `getUserMedia` for the microphone, merges the tracks and creates a `MediaRecorder` (`video/webm;codecs=vp8,opus` when supported, 2.5 Mbit/s), started with a 1000 ms timeslice.
- In Tauri each chunk goes to `save_recording_chunk`; in a browser chunks stay in `recordedChunks`, and a second audio-only `MediaRecorder` fills `audioChunks`.
- `pauseRecording`, `resumeRecording`, `cancelRecording` act on the recorders.
- `stopRecording` returns the `finalize_recording` path in Tauri, or an object URL and stores blobs on `window.__voiceover_blob` and `window.__voiceover_audio_blob`.
- `getAudioDevices` lists `audioinput` devices. Type `CaptureMode` is `fullscreen | window | region`.

## Related
- [[runtime/record-screen-and-voice]]
- [[building-blocks/recording-commands]]
- [[building-blocks/home-screen]]
