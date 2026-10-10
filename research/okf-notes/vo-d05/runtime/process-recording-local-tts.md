---
id: runtime/process-recording-local-tts
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Process recording with local TTS
description: Flow of process_recording when provider is local, using transcribe-then-generate or voice conversion.
domain: architecture
tags:
  - runtime
  - pipeline
  - local-tts
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/pipeline.rs
  - resource: src-tauri/src/local_tts.rs
  - resource: src-tauri/src/sidecar.rs
related:
  - building-blocks/tauri-local-tts-bridge
  - runtime/voice-generation-job
  - runtime/process-recording-elevenlabs
---

# Process recording with local TTS

For provider `local` the pipeline sends audio to the sidecar instead of ElevenLabs.

## Steps

1. `process_recording` (src-tauri/src/pipeline.rs) requires `local_voice_profile_id` and extracts audio as in [[runtime/process-recording-elevenlabs]].
2. `sidecar::ensure_running` returns the sidecar port, restarting it if its health check fails.
3. If `local_tts_mode` is `vc`, `local_tts::voice_convert` posts `source_audio_path` to `/voice-convert`.
4. Otherwise `local_tts::speech_to_speech` uploads the WAV to `/transcribe`, errors on empty text, and writes `transformed-<ts>.txt` with segment and word times.
5. It posts `/generate` with `profile_id`, `text`, `segments` and `original_duration` (the probed video duration when known).
6. `poll_and_download` polls `/generate/{id}/status` every 500 ms until `completed` (error on `error`, timeout 300 s), then downloads `/audio/{id}` into `transformed-<ts>.wav`.
7. `ffmpeg::replace_audio` builds the final MP4.
8. The `.txt` transcript is copied next to the MP4 when present.
9. Temp files are removed and a `Complete` event is sent.

## Related

- [[building-blocks/tauri-local-tts-bridge]] - Rust local TTS bridge
- [[runtime/voice-generation-job]] - Voice generation job in the sidecar
- [[runtime/process-recording-elevenlabs]] - Process recording with ElevenLabs
