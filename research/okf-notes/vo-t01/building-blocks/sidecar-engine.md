---
id: building-blocks/sidecar-engine
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Sidecar Engine Modules
description: Speech engines, text chunking, audio assembly and profile storage in Python.
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
  - resource: src-tauri/sidecar/chunked_tts.py
  - resource: src-tauri/sidecar/profiles.py
relations:
  relates_to:
    - building-blocks/sidecar-server
    - runtime/local-voice-conversion
    - runtime/create-voice-profile
---
# Sidecar Engine Modules

Three modules supply the work that `server.py` schedules.

## `tts.py`

- `transcribe(audio_path, models_dir)` loads `mlx-community/whisper-large-v3-turbo` on first use and returns text, duration and segments with word timestamps.
- `load_qwen_model`, `is_qwen_loaded`, `create_voice_prompt`, `combine_voice_prompts`, `generate_speech`; `_get_device` picks `mps` or `cpu`.
- Voice prompts are cached as `<sha256>.prompt` files by `_cache_key`, `_load_cached_prompt`, `_save_cached_prompt`.

## `chunked_tts.py`

`split_text_into_chunks` (default `DEFAULT_MAX_CHUNK_CHARS = 800`), `concatenate_audio_chunks` (crossfade, default 50 ms), `pad_audio_to_match_timing`, `assemble_timed_segments`, `_fix_degenerate_timestamps`.

## `profiles.py`

Profiles live at `<data_dir>/profiles/<id>/profile.json` with `samples/<id>.wav` and `.txt`. Functions: `list_profiles`, `get_profile`, `create_profile`, `delete_profile`, `add_sample`, `get_samples`; `_validate_profile_id` accepts letters, digits, `_` and `-`.

## Related

- [Sidecar Server](sidecar-server.md)
- [Flow: Local Voice Replacement](../runtime/local-voice-conversion.md)
- [Flow: Create a Voice Profile](../runtime/create-voice-profile.md)
