---
id: runtime/local-voice-generation
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Local voice generation in the sidecar"
description: "Steps the sidecar performs between POST /generate and a downloadable WAV file."
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
  - resource: src-tauri/sidecar/profiles.py
  - resource: src-tauri/sidecar/chunked_tts.py
related:
  - building-blocks/sidecar-engine
  - runtime/process-recording
  - interfaces/sidecar-http-routes
---
# Local voice generation in the sidecar

Generation is queued and handled one job at a time.

## Steps

1. `generate` (server.py) reads `profile_id`, `text`, `language`; it answers 400 if `profile_id` or `text` is empty.
2. It stores `_generations[gen_id]` with status `queued` and puts `(gen_id, _do_generate())` on `_generation_queue`, then returns `{id}`.
3. `_generation_worker` takes the job and sets status `generating`, then `completed` or `failed`.
4. `_do_generate` sets `loading_model` and awaits `tts.load_qwen_model`.
5. `profiles.get_samples` lists the profile samples; none raises `ValueError`.
6. Status `preparing_voice`: `tts.combine_voice_prompts` builds prompts, using the cache folder `<data_dir>/cache`.
7. `chunked_tts.split_text_into_chunks` splits the text; one chunk calls `generate_speech` once, several chunks call it with `seed=i` and join with `concatenate_audio_chunks`.
8. `soundfile.write` saves `<data_dir>/generations/<gen_id>.wav`.
9. Clients poll `GET /generate/{gen_id}/status` and fetch `GET /audio/{gen_id}`.

The transcription used by the Rust pipeline comes from `POST /transcribe` (`tts.transcribe`).

## Related

- [[building-blocks/sidecar-engine]]
- [[runtime/process-recording]]
- [[interfaces/sidecar-http-routes]]
