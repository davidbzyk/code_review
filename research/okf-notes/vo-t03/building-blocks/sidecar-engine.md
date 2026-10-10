---
id: building-blocks/sidecar-engine
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Sidecar speech engine"
description: "Whisper transcription, Qwen voice cloning, profile storage and text chunking."
domain: architecture
tags:
  - building-block
  - python
  - tts
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/sidecar/tts.py
  - resource: src-tauri/sidecar/profiles.py
  - resource: src-tauri/sidecar/chunked_tts.py
related:
  - building-blocks/sidecar-server
  - runtime/local-voice-generation
  - glossary/terms
---
# Sidecar speech engine

Three Python modules do the model work and the on-disk profile storage for the sidecar.

## tts.py

- `transcribe(audio_path, models_dir)` loads `openai/whisper-large-v3-turbo` through `mlx_audio.stt.load` on first use and returns `{text, duration}`.
- `load_qwen_model(models_dir, model_size="1.7B")` loads `Qwen/Qwen3-TTS-12Hz-1.7B-Base` (or 0.6B) in a thread; `is_qwen_loaded`.
- `create_voice_prompt`, `combine_voice_prompts` (keeps only the last prompt item), `generate_speech(text, voice_prompt, language, seed)`.
- Prompt cache files `<md5>.prompt` through `_cache_key`, `_load_cached_prompt`, `_save_cached_prompt`.
- `LANGUAGE_CODE_TO_NAME` maps ten language codes.

## profiles.py

- Profiles are folders `<data_dir>/profiles/<uuid>/` with `profile.json` and `samples/<uuid>.wav` plus `.txt`.
- `list_profiles`, `get_profile`, `create_profile`, `delete_profile`, `add_sample`, `get_samples`.

## chunked_tts.py

- `split_text_into_chunks(text, max_chars=800)` splits at sentence ends, then clause marks, then spaces.
- `concatenate_audio_chunks(chunks, sample_rate, crossfade_ms=50)` joins audio with a linear crossfade.

## Related

- [[building-blocks/sidecar-server]]
- [[runtime/local-voice-generation]]
- [[glossary/terms]]
