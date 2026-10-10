---
id: building-blocks/sidecar-engine
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Sidecar Engine Modules
description: tts.py, chunked_tts.py and profiles.py: speech models, text and audio chunking, and profile storage.
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
  - interfaces/sidecar-http-profiles-models
  - crosscutting/security-boundaries
---

# Sidecar Engine Modules

Three modules hold the model and file logic used by server.py.

## tts.py

- `transcribe(audio_path, models_dir)` loads `mlx-community/whisper-large-v3-turbo` on first use and returns `text`, `duration`, `segments`.
- `_group_words_into_phrases(words, min_pause_sec=0.3)`, `_is_hallucinated`, `_filter_segments`.
- `load_qwen_model(models_dir, model_size="1.7B")` loads `Qwen/Qwen3-TTS-12Hz-1.7B-Base` (or 0.6B); `_get_device` picks `mps` or `cpu`.
- `create_voice_prompt`, `combine_voice_prompts`, `generate_speech(text, voice_prompt, language, seed)`, `is_qwen_loaded`.
- Voice prompts are cached as `{sha256}.prompt` files.

## chunked_tts.py

- `split_text_into_chunks(text, max_chars=800)`, `concatenate_audio_chunks(chunks, sample_rate, crossfade_ms=50)`.
- `pad_audio_to_match_timing(audio, sample_rate, word_timing)`, `assemble_timed_segments(tts_segments, original_duration, sample_rate)`.

## profiles.py

- Profiles live in `{data_dir}/profiles/{uuid}/` with `profile.json` and `samples/{uuid}.wav` plus `.txt`.
- `list_profiles`, `get_profile`, `create_profile`, `delete_profile`, `add_sample`, `get_samples`, `_validate_profile_id` (regex `^[a-zA-Z0-9_-]+$`).

## Related

- [Sidecar Server](./sidecar-server.md)
- [Sidecar HTTP: Profiles and Models](../interfaces/sidecar-http-profiles-models.md)
- [Security Boundaries](../crosscutting/security-boundaries.md)
