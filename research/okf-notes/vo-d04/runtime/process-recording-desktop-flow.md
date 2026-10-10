---
id: runtime/process-recording-desktop-flow
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Process recording in the desktop app"
description: "The process_recording command from invoke to saved MP4."
domain: architecture
tags:
  - runtime
  - pipeline
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
architecture_layer: runtime
sources:
  - resource: src/routes/preview/+page.svelte
  - resource: src-tauri/src/pipeline.rs
  - resource: src-tauri/src/ffmpeg.rs
  - resource: src-tauri/src/elevenlabs.rs
related:
  - building-blocks/route-preview
  - building-blocks/backend-pipeline
  - interfaces/pipeline-events
  - runtime/process-recording-browser-flow
---

# Process recording in the desktop app

In Tauri, `processViaTauri()` hands the recording path to Rust, which writes `voiceover-<secs>.mp4`.

## Steps
1. `processAndSave()` calls `processViaTauri()` (src/routes/preview/+page.svelte).
2. It creates a `Channel`, sets `onmessage`, invokes `process_recording` with `recordingPath`, `voiceReplacement`, `voiceId`, `onEvent` (src/routes/preview/+page.svelte).
3. `process_recording` returns an error if the file is missing, loads config with `config::get_config`, creates the output folder (src-tauri/src/pipeline.rs).
4. Without voice replacement: sends Progress "Saving" 50, runs `ffmpeg::normalize_to_mp4`, sends Complete, removes the input.
5. With it: requires a non-empty API key; picks the voice id from the argument, else the default voice, else the first voice.
6. `ffmpeg::extract_audio` writes `extracted-<ts>.wav` (Progress 5 and 10).
7. `elevenlabs::speech_to_speech` writes `transformed-<ts>.mp3` (Progress 15 and 85).
8. `ffmpeg::replace_audio` writes the final MP4 (Progress 90); Complete is sent and the three temp files are removed.
9. The page stores `outputPath` and sets state `saved` (src/routes/preview/+page.svelte).

## Related

- [[building-blocks/route-preview]]
- [[building-blocks/backend-pipeline]]
- [[interfaces/pipeline-events]]
- [[runtime/process-recording-browser-flow]]
