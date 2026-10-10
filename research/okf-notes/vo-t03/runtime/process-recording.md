---
id: runtime/process-recording
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Process a recording"
description: "Steps the Rust pipeline performs for process_recording, with and without voice replacement."
domain: architecture
tags:
  - runtime
  - pipeline
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/pipeline.rs
  - resource: src-tauri/src/ffmpeg.rs
  - resource: src-tauri/src/elevenlabs.rs
  - resource: src-tauri/src/local_tts.rs
  - resource: src/routes/preview/+page.svelte
related:
  - building-blocks/rust-pipeline
  - interfaces/pipeline-events
  - runtime/local-voice-generation
---
# Process a recording

The preview page calls `process_recording`; Rust writes `voiceover-<timestamp>.mp4` to the configured output folder.

## Steps

1. `processAndSave` (src/routes/preview/+page.svelte) calls `processViaTauri`, which opens a `Channel` and invokes `process_recording`.
2. `process_recording` (src-tauri/src/pipeline.rs) checks the file exists and loads config with `config::get_config`.
3. It creates the output folder, falling back to `<video dir or home>/VoiceOver` if creation fails.
4. Without voice replacement it sends `Progress` "Saving", runs `ffmpeg::normalize_to_mp4`, sends `Complete`, deletes the input.
5. With replacement and provider `local`, it requires `local_voice_profile_id`; otherwise it requires the ElevenLabs key and a voice id (the argument, else the default voice, else the first voice).
6. `ffmpeg::extract_audio` writes `extracted-<timestamp>.wav`.
7. Provider `local`: `sidecar::ensure_running`, then `local_tts::speech_to_speech` (transcribe, generate, poll, download). Provider ElevenLabs: `elevenlabs::speech_to_speech`.
8. `ffmpeg::replace_audio` muxes the new audio with the video.
9. It sends `Complete`, then removes the recording, extracted and transformed files.

The browser path instead calls ElevenLabs from the page and splices with ffmpeg.wasm (`processViaBrowser`).

## Related

- [[building-blocks/rust-pipeline]]
- [[interfaces/pipeline-events]]
- [[runtime/local-voice-generation]]
