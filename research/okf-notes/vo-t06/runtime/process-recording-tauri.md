---
id: runtime/process-recording-tauri
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Process Recording, Desktop"
description: "The desktop path from the preview button to an MP4 on disk."
domain: architecture
tags:
  - runtime
  - pipeline
  - desktop
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/preview/+page.svelte
  - resource: src-tauri/src/pipeline.rs
  - resource: src-tauri/src/ffmpeg.rs
  - resource: src-tauri/src/elevenlabs.rs
relations:
  relates_to:
    - building-blocks/rust-pipeline
    - interfaces/tauri-events
    - runtime/drive-upload
---

In Tauri, processing runs in Rust with progress events sent to the page.

## Steps

1. `processAndSave()` in `src/routes/preview/+page.svelte` calls `processViaTauri()`.
2. It creates a `Channel` and invokes `process_recording` with `recordingPath`, `voiceReplacement`, `voiceId` and `onEvent`.
3. `process_recording` (`src-tauri/src/pipeline.rs`) loads config with `config::get_config` and prepares the output folder.
4. Voice replacement off: `ffmpeg::normalize_to_mp4` writes `voiceover-<secs>.mp4`.
5. Voice replacement on: `ffmpeg::extract_audio` writes `extracted-<secs>.wav` next to the recording.
6. `elevenlabs::speech_to_speech` posts the WAV and writes `transformed-<secs>.mp3`.
7. `ffmpeg::replace_audio` combines the original video and the new audio into the MP4.
8. The function sends `Progress` and `Complete` events and removes temp files with `cleanup_temp`.
9. The channel handler updates `appState.processingProgress`, `processingStage`, `outputPath`; `recordingState` becomes `saved`.

## Related

- [Rust pipeline](../building-blocks/rust-pipeline.md)
- [Tauri events and channels](../interfaces/tauri-events.md)
- [Drive upload flow](drive-upload.md)
