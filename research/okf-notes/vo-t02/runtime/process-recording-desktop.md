---
id: runtime/process-recording-desktop
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Process Recording on Desktop"
description: "The Rust pipeline from a recorded file to a final MP4."
domain: architecture
tags:
  - runtime
  - pipeline
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/preview/+page.svelte
  - resource: src-tauri/src/pipeline.rs
  - resource: src-tauri/src/ffmpeg.rs
  - resource: src-tauri/src/elevenlabs.rs
  - resource: src-tauri/src/local_tts.rs
related:
  - runtime/process-recording-browser
  - interfaces/events-and-channels
  - building-blocks/backend-pipeline-and-ffmpeg
---
# Process Recording on Desktop

`process_recording` runs ffmpeg and a provider and reports progress on a channel.

## Steps
1. `processAndSave` then `processViaTauri` (src/routes/preview/+page.svelte) create a `Channel` and invoke `process_recording` with `recordingPath`, `voiceReplacement`, `voiceId`.
2. `process_recording` (src-tauri/src/pipeline.rs) checks the file exists and calls `config::get_config`.
3. It creates `output_dir`; if that fails it falls back to a `VoiceOver` folder under the video or home directory.
4. Without voice replacement it sends `Progress` "Saving" at 50, runs `ffmpeg::normalize_to_mp4`, sends `Complete` and returns `voiceover-<unix seconds>.mp4`.
5. With replacement it requires the ElevenLabs key and a voice id, or for provider `local` a `local_voice_profile_id`.
6. `ffmpeg::extract_audio` writes a 16 kHz mono WAV (progress 5 then 10).
7. `elevenlabs::speech_to_speech` or `local_tts::speech_to_speech` writes the transformed audio (progress 15 then 85).
8. `ffmpeg::replace_audio` maps video from input 0 and audio from input 1, encodes libx264 and aac (progress 90).
9. It sends `Complete`, deletes the temp files with `cleanup_temp`, returns the path.

## Related
- [Process Recording in the Browser](./process-recording-browser.md)
- [Events and Channels](../interfaces/events-and-channels.md)
- [Backend Pipeline and ffmpeg](../building-blocks/backend-pipeline-and-ffmpeg.md)
