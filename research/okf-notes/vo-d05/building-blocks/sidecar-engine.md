---
id: building-blocks/sidecar-engine
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Sidecar engine modules
description: tts.py, chunked_tts.py and profiles.py hold the model calls, audio assembly and voice profile storage.
domain: architecture
tags:
  - building-block
  - python
  - sidecar
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/sidecar/tts.py
  - resource: src-tauri/sidecar/chunked_tts.py
  - resource: src-tauri/sidecar/profiles.py
related:
  - building-blocks/sidecar-server
  - runtime/voice-generation-job
  - crosscutting/state
---

# Sidecar engine modules

Three Python modules back the routes in `server.py`.

## tts.py

- `transcribe(audio_path, models_dir)` loads `mlx-community/whisper-large-v3-turbo` on first use and returns text, duration and segments with word timestamps.
- `load_qwen_model(models_dir, model_size="1.7B")`, `is_qwen_loaded()`, `_get_device()` (mps or cpu).
- `create_voice_prompt`, `combine_voice_prompts` (keeps the last sample's prompt), `generate_speech(text, voice_prompt, language, seed)`.
- Voice prompts are cached as `<sha256>.prompt` files by `_cache_key`, `_load_cached_prompt`, `_save_cached_prompt`.

## chunked_tts.py

- `DEFAULT_MAX_CHUNK_CHARS = 800`; `split_text_into_chunks`.
- `concatenate_audio_chunks(chunks, sample_rate, crossfade_ms=50)`.
- `pad_audio_to_match_timing(audio, sample_rate, word_timing)` inserts silence by word timing.
- `assemble_timed_segments(tts_segments, original_duration, sample_rate)` places segments at original timestamps.

## profiles.py

- Profiles live under `<data-dir>/profiles/<uuid>/` with `profile.json` and `samples/<uuid>.wav` plus `.txt`.
- `list_profiles`, `get_profile`, `create_profile`, `delete_profile`, `add_sample`, `get_samples`; `_validate_profile_id` allows `[a-zA-Z0-9_-]+`.

## Used by

- [[building-blocks/sidecar-server]], in the job described in [[runtime/voice-generation-job]].

## Related

- [[building-blocks/sidecar-server]] - Sidecar server
- [[runtime/voice-generation-job]] - Voice generation job in the sidecar
- [[crosscutting/state]] - State and storage
