---
id: runtime/process-recording-elevenlabs
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Flow: Process a Recording (ElevenLabs)
description: The `process_recording` steps when the provider is elevenlabs or voice replacement is off.
domain: architecture
tags:
  - runtime
  - pipeline
  - elevenlabs
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/preview/+page.svelte
  - resource: src-tauri/src/pipeline.rs
  - resource: src-tauri/src/ffmpeg.rs
  - resource: src-tauri/src/elevenlabs.rs
related:
  - building-blocks/rust-pipeline
  - building-blocks/rust-tts-providers
  - interfaces/tauri-events-and-channels
  - runtime/process-recording-local
---

# Flow: Process a Recording (ElevenLabs)

Trigger: `/preview` calls `processAndSave`, which calls `processViaTauri` and `invoke('process_recording', ...)` with a `Channel`.

1. `process_recording` (src-tauri/src/pipeline.rs) checks that the file exists and loads `config::get_config`.
2. It creates the output dir, or falls back to `<videos>/VoiceOver`, and names the file `voiceover-{timestamp}.mp4`.
3. If `voice_replacement` is false: it sends `Progress` "Saving", calls `ffmpeg::normalize_to_mp4`, sends `Complete`, calls `cleanup_temp`, and returns.
4. Otherwise it requires a non-empty `elevenlabs_api_key` and a voice id (argument, default voice, or first voice).
5. It sends `Progress` "Extracting audio", calls `ffmpeg::probe_duration`, then `ffmpeg::extract_audio` to `extracted-{timestamp}.wav`.
6. It sends `Progress` 15 percent and calls `elevenlabs::speech_to_speech` to write `transformed-{timestamp}.mp3`.
7. It sends `Progress` 85, then 90 "Assembling video", and calls `ffmpeg::replace_audio`.
8. It sends `Complete { output_path }`, removes temp files, and calls `cleanup_stale_recordings(3600 s)`.
9. In the page, the channel handler sets `appState.outputPath` and state `saved`.

## Related

- [Rust Pipeline and ffmpeg](../building-blocks/rust-pipeline.md)
- [Rust TTS Providers and Models](../building-blocks/rust-tts-providers.md)
- [Channels and Window Events](../interfaces/tauri-events-and-channels.md)
- [Flow: Process a Recording (Local TTS)](./process-recording-local.md)
