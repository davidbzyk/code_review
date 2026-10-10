---
id: runtime/record-screen
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Flow: Record the Screen
description: How a recording starts, streams chunks to disk, and stops.
domain: architecture
tags:
  - runtime
  - recording
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/+page.svelte
  - resource: src/lib/recorder.svelte.ts
  - resource: src-tauri/src/commands/recording.rs
related:
  - building-blocks/frontend-recorder
  - building-blocks/rust-recording-commands
  - runtime/process-recording-elevenlabs
---

# Flow: Record the Screen

Trigger: the user presses record on `/`.

1. `handleRecord` (src/routes/+page.svelte) sets state `selecting` and calls `startRecording`.
2. `startRecording` (src/lib/recorder.svelte.ts) makes a `sessionId` with `generateSessionId` and calls `navigator.mediaDevices.getDisplayMedia`.
3. Under Tauri, unless the mode is `window`, it minimizes the window after requesting the picker (`getCurrentWindow().minimize()`), then unminimizes and focuses it.
4. In `region` mode it grabs a frame, shows `RegionSelector`, and waits for `confirmRegionSelection`.
5. It opens the microphone with `getUserMedia`, optionally the webcam, and builds a combined `MediaStream`.
6. It creates `MediaRecorder` and calls `start(5000)`.
7. Each `ondataavailable` calls `save_recording_chunk` with `sessionId`, bytes, `chunkIndex` (`save_recording_chunk`, src-tauri/src/commands/recording.rs).
8. `handleRecord` sets state `recording` and starts a one-second timer.
9. Pause and resume call `pauseRecording` and `resumeRecording`.
10. `handleStop` calls `stopRecording`, which on `onstop` calls `finalize_recording`; the command joins `chunk_*.webm` files into `<session>.webm` and returns the path.
11. `handleStop` stores the path in `appState.recordingPath`, sets state `recorded`, and calls `goto('/preview')`.

Without Tauri, chunks stay in memory and `stopRecording` stores blobs with `blobStore.setVideo` and `setAudio`.

## Related

- [Frontend Recorder](../building-blocks/frontend-recorder.md)
- [Rust Recording Commands](../building-blocks/rust-recording-commands.md)
- [Flow: Process a Recording (ElevenLabs)](./process-recording-elevenlabs.md)
