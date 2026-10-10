---
id: runtime/process-recording-local
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Flow: Process a Recording (Local TTS)
description: The pipeline branch used when config.provider is local.
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
  - resource: src-tauri/sidecar/server.py
related:
  - building-blocks/rust-tts-providers
  - building-blocks/sidecar-server
  - runtime/process-recording-elevenlabs
  - interfaces/sidecar-http-generation
---

# Flow: Process a Recording (Local TTS)

Trigger: `process_recording` with `config.provider == "local"` (src-tauri/src/pipeline.rs).

1. It requires `local_voice_profile_id`.
2. It extracts the WAV as in the ElevenLabs flow and sends `Progress` "Transforming voice (local)...".
3. `sidecar::ensure_running` returns the port (src-tauri/src/sidecar.rs).
4. If `local_tts_mode` is `Vc`, `local_tts::voice_convert` posts `/voice-convert`; otherwise `local_tts::speech_to_speech` runs.
5. `speech_to_speech` posts the WAV to `/transcribe` (`transcribe`, server.py), writes `transformed-*.txt`, and posts `/generate` with `profile_id`, `text`, `segments`, `original_duration`.
6. The server queues `_do_generate` in `_generation_queue`; the worker loads the Qwen model, builds a voice prompt from profile samples, and generates per segment.
7. `assemble_timed_segments` places audio at the original timestamps and `_run_generation` saves the WAV.
8. `poll_and_download` polls `/generate/{id}/status`, then GETs `/audio/{id}` and writes the output WAV.
9. `ffmpeg::replace_audio` joins the video and new audio.
10. If `transformed-*.txt` exists, it is copied next to the MP4 as `.txt`.
11. `Complete` is sent and temp files are removed.

`video_duration` from `probe_duration` is passed as the `original_duration`.

## Related

- [Rust TTS Providers and Models](../building-blocks/rust-tts-providers.md)
- [Sidecar Server](../building-blocks/sidecar-server.md)
- [Flow: Process a Recording (ElevenLabs)](./process-recording-elevenlabs.md)
- [Sidecar HTTP: Transcribe, Generate, Audio, Convert, YouTube](../interfaces/sidecar-http-generation.md)
