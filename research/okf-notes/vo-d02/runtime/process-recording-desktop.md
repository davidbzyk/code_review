---
id: runtime/process-recording-desktop
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Runtime: process a recording (desktop)
description: Flow of process_recording in Rust with progress events to the preview page.
domain: architecture
tags:
  - runtime
  - arc42-6
  - pipeline
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/preview/+page.svelte
  - resource: src-tauri/src/pipeline.rs
  - resource: src-tauri/src/ffmpeg.rs
  - resource: src-tauri/src/elevenlabs.rs
  - resource: src-tauri/src/config.rs
related:
  - building-blocks/backend-pipeline
  - building-blocks/frontend-preview-page
  - interfaces/pipeline-event
  - runtime/process-recording-browser
---

The preview page invokes `process_recording`, which runs ffmpeg and ElevenLabs and reports through a `Channel`.

1. `processAndSave()` in src/routes/preview/+page.svelte calls `processViaTauri()`, which invokes `process_recording`.
2. `process_recording` (src-tauri/src/pipeline.rs) returns an error when the recording file does not exist, loads config with `config::get_config`, creates `output_dir`, and names the file `voiceover-<unix seconds>.mp4`.
3. Without voice replacement: sends `Progress` "Saving" 50, runs `ffmpeg::normalize_to_mp4`, sends `Complete`, removes the input, returns the path.
4. With voice replacement: errors when `elevenlabs_api_key` is empty or no voice exists; the voice is the one with `is_default`, else the first.
5. Stage "Extracting audio": `ffmpeg::extract_audio` to `extracted-<ts>.wav` (src-tauri/src/ffmpeg.rs).
6. Stage "Transforming voice": `elevenlabs::speech_to_speech` to `transformed-<ts>.mp3` (src-tauri/src/elevenlabs.rs).
7. Stage "Assembling video": `ffmpeg::replace_audio` writes the final MP4.
8. Sends `Complete { output_path }`, removes the recording and both temp files, returns the path.
9. The page's `onEvent.onmessage` updates `processingProgress` and `processingStage`; on return sets `outputPath` and state `saved`.

## Related
[[building-blocks/backend-pipeline]], [[building-blocks/frontend-preview-page]], [[interfaces/pipeline-event]], [[runtime/process-recording-browser]]
