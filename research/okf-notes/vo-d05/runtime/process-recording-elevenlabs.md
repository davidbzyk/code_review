---
id: runtime/process-recording-elevenlabs
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Process recording with ElevenLabs
description: Flow of the process_recording command when voice replacement uses the ElevenLabs provider.
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
  - building-blocks/tauri-media-pipeline
  - runtime/process-recording-local-tts
  - runtime/browser-mode-pipeline
---

# Process recording with ElevenLabs

`processViaTauri` invokes `process_recording`, which runs the stages below and reports progress on a `Channel<PipelineEvent>`.

## Steps

1. `processViaTauri` (src/routes/preview/+page.svelte) creates a `Channel`, then invokes `process_recording` with `recordingPath`, `voiceReplacement`, `voiceId`, `onEvent`.
2. `process_recording` (src-tauri/src/pipeline.rs) loads config with `config::get_config` and creates `output_dir`.
3. With voice replacement off, `ffmpeg::normalize_to_mp4` writes `voiceover-<ts>.mp4`, a `Complete` event is sent, and the temp file is removed.
4. With replacement on and provider `elevenlabs`, it requires a non-empty API key and a voice id (given, default voice, or first voice).
5. `ffmpeg::probe_duration` reads the video duration.
6. `ffmpeg::extract_audio` writes `extracted-<ts>.wav` (progress 5 to 10).
7. `elevenlabs::speech_to_speech` posts the WAV as multipart (`model_id`, `remove_background_noise=true`) to the voice URL from `s2s_url` and saves `transformed-<ts>.mp3` (progress 15 to 85).
8. `ffmpeg::replace_audio` muxes the original video with the new audio into the final MP4 (progress 90).
9. A `Complete` event is sent, temp files are removed, and `cleanup_stale_recordings` runs.
10. The page sets `outputPath` and state `saved`.

## Related

- [[building-blocks/tauri-media-pipeline]] - Rust media pipeline
- [[runtime/process-recording-local-tts]] - Process recording with local TTS
- [[runtime/browser-mode-pipeline]] - Browser mode pipeline
