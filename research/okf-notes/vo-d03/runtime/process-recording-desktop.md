---
id: runtime/process-recording-desktop
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Flow: process a recording in the desktop app"
description: "Steps from Save on the preview page to the final MP4 and progress events."
domain: architecture
tags:
  - runtime
  - pipeline
  - tauri
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/preview/+page.svelte
  - resource: src-tauri/src/pipeline.rs
  - resource: src-tauri/src/ffmpeg.rs
  - resource: src-tauri/src/elevenlabs.rs
  - resource: src-tauri/src/config.rs
relations:
  relates_to:
    - building-blocks/backend-pipeline
    - interfaces/pipeline-events
---

# Flow: process a recording in the desktop app

This flow runs when `isTauri()` is true and the user presses the process button.

## Steps

1. `processAndSave()` in `src/routes/preview/+page.svelte` calls `processViaTauri()`.
2. `processViaTauri()` creates a `Channel` and invokes `process_recording` with `recordingPath`, `voiceReplacement`, `voiceId` and `onEvent`.
3. `process_recording` in `src-tauri/src/pipeline.rs` checks the file exists and calls `config::get_config`.
4. It creates `output_dir`, or falls back to the video or home directory plus `VoiceOver`.
5. Without voice replacement: sends `Progress` "Saving" 50, runs `ffmpeg::normalize_to_mp4`, sends `Complete`, deletes the temp recording.
6. With voice replacement: errors if the API key or voice is missing.
7. `ffmpeg::extract_audio` writes `extracted-<ts>.wav`; progress 5 then 10.
8. `elevenlabs::speech_to_speech` writes `transformed-<ts>.mp3`; progress 15 then 85.
9. `ffmpeg::replace_audio` writes `voiceover-<ts>.mp4`; progress 90.
10. It sends `Complete { output_path }` and removes the three temp files.
11. The page receives events in `onEvent.onmessage`, updates `appState.processingProgress`, `processingStage`, `outputPath`, and sets `recordingState = 'saved'`.

## Related

- [building-blocks/backend-pipeline](../building-blocks/backend-pipeline.md)
- [building-blocks/page-preview](../building-blocks/page-preview.md)
- [interfaces/pipeline-events](../interfaces/pipeline-events.md)
- [runtime/process-recording-browser](./process-recording-browser.md)
