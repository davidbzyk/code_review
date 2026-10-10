---
id: building-blocks/sidecar-server
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Sidecar server
description: server.py is the FastAPI app that exposes transcription, generation, profiles and model routes.
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
  - interfaces/sidecar-http-routes
  - building-blocks/sidecar-engine
  - runtime/sidecar-startup
  - runtime/voice-generation-job
---

# Sidecar server

`server.py` creates `app = FastAPI(title="VoiceOver TTS Sidecar")` and a serial generation queue.

## Facts

- `main()` parses `--host` (default 127.0.0.1), `--port`, `--data-dir`, `--parent-pid`, `--ffmpeg`; sets `HF_HUB_CACHE` to `<data-dir>/models`; adds the ffmpeg folder to PATH; starts `_start_parent_watchdog`; runs `uvicorn`.
- `_start_parent_watchdog(parent_pid)` checks the parent every 2 s and sends SIGTERM (or `os._exit` on Windows) after it is gone for 1 s.
- `_generations` maps id to `{status, error, audio_path}`; `_generation_queue` and `_generation_worker` run one job at a time; `_run_generation` writes `<data-dir>/generations/<id>.wav`.
- `_cleanup_generations` drops finished jobs older than one hour; `_periodic_cleanup` runs every 300 s.
- `_validate_path` limits file paths to the data dir and the system temp dir.
- `error_response(status, message)` returns `{"error": message}`.
- `/voice-convert` loads `mlx-community/Fun-CosyVoice3-0.5B-2512-8bit` and converts in chunks of 25 s.
- `/extract-youtube` accepts only https URLs on youtube.com, www.youtube.com, m.youtube.com, youtu.be, downloads with yt-dlp and runs ffmpeg.

## Uses

- Engine and storage modules ([[building-blocks/sidecar-engine]]). Routes: [[interfaces/sidecar-http-routes]].

## Related

- [[interfaces/sidecar-http-routes]] - Sidecar HTTP routes
- [[building-blocks/sidecar-engine]] - Sidecar engine modules
- [[runtime/sidecar-startup]] - Sidecar startup
- [[runtime/voice-generation-job]] - Voice generation job in the sidecar
