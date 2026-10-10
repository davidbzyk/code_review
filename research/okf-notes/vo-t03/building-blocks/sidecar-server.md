---
id: building-blocks/sidecar-server
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Sidecar HTTP server"
description: "The FastAPI app that exposes health, transcription, generation, profile, model and YouTube routes."
domain: architecture
tags:
  - building-block
  - python
  - fastapi
  - sidecar
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/sidecar/server.py
related:
  - interfaces/sidecar-http-routes
  - building-blocks/sidecar-engine
  - runtime/local-voice-generation
  - deployment/sidecar-packaging
  - building-blocks/rust-sidecar-client
---
# Sidecar HTTP server

`server.py` is the sidecar entry point; it is run with uvicorn and frozen with PyInstaller.

## Facts

- Command line options `--host`, `--port`, `--data-dir`, `--parent-pid`, `--ffmpeg` (`main`).
- `lifespan` starts `_generation_worker`, which takes `(gen_id, coroutine)` pairs from `_generation_queue` one at a time.
- `_generations` is an in-process dict of `status`, `error`, `audio_path`.
- `_start_parent_watchdog(parent_pid)` checks `_is_pid_alive` every 2 seconds and sends SIGTERM (or `os._exit(0)` on Windows) after the parent is gone for 1 second; it logs to `<data_dir>/logs/watchdog.log`.
- `main` sets `HF_HUB_CACHE` to `<data_dir>/models` and prepends the ffmpeg directory to `PATH`.
- A patch wraps `transformers.utils.generic.check_model_inputs` so it works with and without parentheses.
- Route handlers are listed in [[interfaces/sidecar-http-routes]].

## Uses

`tts.py`, `profiles.py`, `chunked_tts.py` ([[building-blocks/sidecar-engine]]), `yt_dlp`, `huggingface_hub`, the `ffmpeg` command.

## Related

- [[runtime/local-voice-generation]]
- [[deployment/sidecar-packaging]]
- [[building-blocks/rust-sidecar-client]]
