---
id: building-blocks/sidecar-server
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Sidecar Server
description: The FastAPI server that hosts transcription, generation, profiles and model downloads.
domain: architecture
tags:
  - building-block
  - python
  - sidecar
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/sidecar/server.py
relations:
  relates_to:
    - interfaces/sidecar-http-api
    - building-blocks/sidecar-engine
    - runtime/local-voice-conversion
    - runtime/sidecar-startup
    - building-blocks/rust-local-tts-and-sidecar
---
# Sidecar Server

`server.py` defines the FastAPI `app` and the serial job queue behind its generation routes.

## Structure

- `main()` parses `--host`, `--port`, `--data-dir`, `--parent-pid`, `--ffmpeg`, sets `HF_HUB_CACHE` to `<data-dir>/models`, starts `_start_parent_watchdog`, and runs `uvicorn.run`.
- `lifespan` starts `_generation_worker` and `_periodic_cleanup`.
- `_generation_queue` is an `asyncio.Queue`; jobs run one at a time. `_generations` maps id to status, error and audio path.
- `_run_generation` writes `<data-dir>/generations/<id>.wav` with `soundfile`.
- `_do_generate` runs Qwen TTS per segment or per text chunk; `_do_voice_convert` runs CosyVoice3 in 25 second chunks with 1 second overlap.
- `_cleanup_generations` removes finished jobs older than 3600 seconds.
- `_validate_path` and `error_response` are helpers.
- The watchdog thread checks `_is_pid_alive(parent_pid)` every 2 seconds and sends SIGTERM when the parent is gone.

## Uses

`tts.py`, `chunked_tts.py`, `profiles.py`, `yt_dlp`, `huggingface_hub`.

## Related

- [Sidecar HTTP API](../interfaces/sidecar-http-api.md)
- [Sidecar Engine Modules](sidecar-engine.md)
- [Flow: Local Voice Replacement](../runtime/local-voice-conversion.md)
- [Flow: Sidecar Startup and Health](../runtime/sidecar-startup.md)
- [Rust Local TTS and Sidecar Manager](rust-local-tts-and-sidecar.md)
