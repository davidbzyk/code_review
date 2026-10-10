---
id: runtime/local-voice-conversion
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Flow: Local Voice Replacement
description: How the sidecar transcribes, generates and returns replacement audio.
domain: architecture
tags:
  - runtime
  - flow
  - sidecar
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/local_tts.rs
  - resource: src-tauri/sidecar/server.py
  - resource: src-tauri/sidecar/tts.py
  - resource: src-tauri/sidecar/chunked_tts.py
  - resource: src-tauri/sidecar/profiles.py
relations:
  relates_to:
    - building-blocks/rust-local-tts-and-sidecar
    - building-blocks/sidecar-server
    - building-blocks/sidecar-engine
    - runtime/record-and-process-recording
---
# Flow: Local Voice Replacement

This flow runs inside `process_recording` when the provider is `local`.

Text-to-speech mode (`local_tts::speech_to_speech`):

1. POST the WAV to `/transcribe` (`transcribe` in `src-tauri/sidecar/server.py`, `tts.transcribe`).
2. Write a `.txt` transcript beside the output file.
3. POST `profile_id`, `text`, `segments` and `original_duration` to `/generate`.
4. `_do_generate` loads the Qwen model with `load_qwen_model`, reads samples with `profiles.get_samples`, builds a prompt with `combine_voice_prompts`.
5. For each segment it calls `generate_speech`, `pad_audio_to_match_timing`, and finally `assemble_timed_segments`.
6. The job is queued; `_generation_worker` runs `_run_generation` and saves a WAV.
7. `poll_and_download` polls `/generate/{id}/status` every 500 ms up to 300 s, then GETs `/audio/{id}`.

Voice conversion mode (`local_tts::voice_convert`):

1. POST `profile_id`, `source_audio_path`, `original_duration` to `/voice-convert`; `_validate_path` restricts the path.
2. `_do_voice_convert` loads `mlx-community/Fun-CosyVoice3-0.5B-2512-8bit`, splits long audio into 25 second chunks with 1 second overlap, and joins them with `concatenate_audio_chunks` (500 ms crossfade).
3. The output is padded or cut to `original_duration`.
4. `poll_and_download` retrieves the WAV.

## Related

- [Rust Local TTS and Sidecar Manager](../building-blocks/rust-local-tts-and-sidecar.md)
- [Sidecar Server](../building-blocks/sidecar-server.md)
- [Sidecar Engine Modules](../building-blocks/sidecar-engine.md)
- [Flow: Record and Process a Recording](record-and-process-recording.md)
