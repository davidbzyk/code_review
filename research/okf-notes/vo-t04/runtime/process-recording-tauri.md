---
id: runtime/process-recording-tauri
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Process recording in Tauri"
description: "In the desktop app, process_recording either converts to MP4 or replaces the voice through ElevenLabs and ffmpeg."
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
relations:
  relates_to:
    - building-blocks/rust-media-pipeline
    - building-blocks/rust-elevenlabs
    - interfaces/tauri-events-and-channels
---
# Process recording in Tauri

The preview page calls one command and receives progress events over a channel.

## Steps

1. `processAndSave()` calls `processViaTauri()` when `isTauri()` (src/routes/preview/+page.svelte).
2. It creates a `Channel`, sets `onmessage` to update `appState.processingProgress` and `processingStage`, and invokes `process_recording` with `recordingPath`, `voiceReplacement`, `voiceId` and the channel.
3. `process_recording` returns an error if the file is missing, then loads config with `config::get_config` (src-tauri/src/pipeline.rs).
4. It creates `output_dir`; if that fails it falls back to `<Videos or home>/VoiceOver`.
5. The final name is `voiceover-<unix seconds>.mp4`.
6. With voice replacement off, it sends a `Progress` event ("Saving", 50), runs `ffmpeg::normalize_to_mp4`, sends `Complete`, deletes the input and returns the path.
7. With it on, it requires a non-empty API key and picks a voice: the argument, else the default voice, else the first voice.
8. `ffmpeg::extract_audio` writes a 16 kHz mono WAV (src-tauri/src/ffmpeg.rs).
9. `elevenlabs::speech_to_speech` posts the WAV and writes an MP3 (src-tauri/src/elevenlabs.rs).
10. `ffmpeg::replace_audio` muxes the video with the MP3 into the MP4.
11. It sends `Complete`, removes the recording, WAV and MP3, and returns the path; the page sets `outputPath` and state `saved`.

## Related

[[building-blocks/rust-media-pipeline]], [[building-blocks/rust-elevenlabs]], [[interfaces/tauri-events-and-channels]]
