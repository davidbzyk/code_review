---
id: runtime/voice-generation-job
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Voice generation job in the sidecar
description: How POST /generate queues a job, builds audio per segment and exposes the WAV for download.
domain: architecture
tags:
  - runtime
  - sidecar
  - tts
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/sidecar/server.py
  - resource: src-tauri/sidecar/tts.py
  - resource: src-tauri/sidecar/chunked_tts.py
  - resource: src-tauri/sidecar/profiles.py
related:
  - building-blocks/sidecar-engine
  - building-blocks/sidecar-server
  - runtime/process-recording-local-tts
---

# Voice generation job in the sidecar

`generate` in server.py answers at once with an id and runs the work later in `_generation_worker`.

## Steps

1. `generate` requires `profile_id` and `text`, creates a uuid, stores `{status: "queued"}`, and puts `_run_generation(gen_id, _do_generate)` on `_generation_queue`.
2. The worker runs one job at a time; status moves through `loading_model`, `preparing_voice`, `generating`.
3. `load_qwen_model` (src-tauri/sidecar/tts.py) loads `Qwen/Qwen3-TTS-12Hz-1.7B-Base`.
4. `get_samples` (profiles.py) lists the profile samples; `combine_voice_prompts` builds the voice prompt.
5. With `segments` and `original_duration`, each segment is spoken by `generate_speech` (sub-chunked by `split_text_into_chunks`), spaced by `pad_audio_to_match_timing`, and placed by `assemble_timed_segments`.
6. Without segments, text is chunked, joined with `concatenate_audio_chunks`, and padded or cut to `original_duration`.
7. `_run_generation` writes `<data-dir>/generations/<id>.wav` with `soundfile` and sets status `completed`, or `error` with the message.
8. `generation_status` returns `{status, error}`; `get_audio` returns the WAV bytes.

## Related

- [[building-blocks/sidecar-engine]] - Sidecar engine modules
- [[building-blocks/sidecar-server]] - Sidecar server
- [[runtime/process-recording-local-tts]] - Process recording with local TTS
