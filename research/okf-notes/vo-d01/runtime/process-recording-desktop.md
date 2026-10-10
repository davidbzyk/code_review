---
id: runtime/process-recording-desktop
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Process Recording on Desktop"
description: "The Rust pipeline that produces the final MP4."
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
---
# Process Recording on Desktop

`processViaTauri` invokes `process_recording`, which branches on `voice_replacement`.

## Steps
1. `processViaTauri` (src/routes/preview/+page.svelte) creates a `Channel` and invokes `process_recording`.
2. `process_recording` (src-tauri/src/pipeline.rs) checks the file exists, loads config, creates `output_dir` and names `voiceover-{timestamp}.mp4`.
3. Without voice replacement: sends Progress "Saving" 50, runs `ffmpeg::normalize_to_mp4`, sends Complete, cleans up.
4. With it: requires a non-empty API key and a voice (default voice, else first).
5. `ffmpeg::extract_audio` writes `extracted-{timestamp}.wav` next to the recording.
6. `elevenlabs::speech_to_speech` writes `transformed-{timestamp}.mp3`.
7. `ffmpeg::replace_audio` writes the final MP4.
8. Sends Complete and removes the three temp files; returns the path.
9. The frontend sets `outputPath` and state `saved`.

## Related
- [[building-blocks/media-pipeline]]
- [[interfaces/pipeline-channel-events]]
- [[runtime/process-recording-browser]]
