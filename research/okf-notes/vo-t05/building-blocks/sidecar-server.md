---
id: building-blocks/sidecar-server
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Sidecar Server
description: The FastAPI process that exposes transcription, generation, profiles, models and YouTube extraction.
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
related:
  - interfaces/sidecar-http-generation
  - interfaces/sidecar-http-profiles-models
  - building-blocks/sidecar-engine
  - runtime/sidecar-startup
---

# Sidecar Server

`server.py` is the single entry file of the sidecar; `main()` parses arguments and runs `uvicorn.run(app, host, port)`.

## Facts

- Arguments: `--host` (default `127.0.0.1`), `--port`, `--data-dir`, `--parent-pid`, `--ffmpeg`.
- `main` sets `DATA_DIR`, sets `HF_HUB_CACHE` to `DATA_DIR/models`, and prepends the ffmpeg folder to `PATH`.
- `_start_parent_watchdog(parent_pid)` runs a daemon thread; `_is_pid_alive` checks the PID; the sidecar stops when the parent is gone after a 1 second grace.
- `lifespan` starts `_generation_worker` and `_periodic_cleanup`.
- `_generation_queue` is an `asyncio.Queue`; generations run one at a time. `_generations` maps id to status.
- `_do_generate` and `_do_voice_convert` produce `(audio, sample_rate, label)` for `_run_generation`, which writes `generations/{id}.wav`.
- `_validate_path` limits file paths to `DATA_DIR` or the system temp dir.
- `_is_model_downloaded` scans the HuggingFace cache.
- `error_response(status, message)` returns `{"error": message}`.
- The voice-conversion model id is `mlx-community/Fun-CosyVoice3-0.5B-2512-8bit`.

## Imports

`tts`, `profiles`, `chunked_tts` are imported inside the handlers.

## Related

- [Sidecar HTTP: Transcribe, Generate, Audio, Convert, YouTube](../interfaces/sidecar-http-generation.md)
- [Sidecar HTTP: Profiles and Models](../interfaces/sidecar-http-profiles-models.md)
- [Sidecar Engine Modules](./sidecar-engine.md)
- [Flow: Sidecar Startup and Shutdown](../runtime/sidecar-startup.md)
