---
id: runtime/sidecar-startup
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Sidecar startup
description: How the Rust host starts the Python sidecar, waits for health and keeps it alive.
domain: architecture
tags:
  - runtime
  - sidecar
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/lib.rs
  - resource: src-tauri/src/sidecar.rs
  - resource: src-tauri/sidecar/server.py
related:
  - building-blocks/tauri-local-tts-bridge
  - building-blocks/sidecar-server
  - building-blocks/tauri-core
---

# Sidecar startup

The sidecar starts in the background during app setup and is restarted on demand.

## Steps

1. Setup in `run()` (src-tauri/src/lib.rs) spawns `sidecar::start_sidecar` on the async runtime.
2. `start_sidecar_inner` (src-tauri/src/sidecar.rs) calls `find_available_port` (bind to port 0), reads `app_data_dir`, and resolves `resolve_ffmpeg_path`.
3. `resolve_sidecar_path` returns the bundled `voiceover-tts` next to the executable in release builds; in debug builds it returns none.
4. Without a binary, `resolve_dev_server_path` finds `sidecar/server.py` and runs it with `.sidecar-venv/bin/python3`, a local `.venv`, or `python3`.
5. Arguments passed: `--port`, `--data-dir`, `--parent-pid`, `--ffmpeg`.
6. `main()` in server.py sets paths, starts the parent watchdog, and runs uvicorn.
7. The host polls `health_check(port)` (GET `/health`, expects `status` = `healthy`) every 500 ms up to 60 s; it kills the child on timeout and reports an exit during startup.
8. Later calls use `ensure_running`: wait if `starting`, reuse a healthy port, otherwise `stop_sidecar_inner` then `start_sidecar`.

## Related

- [[building-blocks/tauri-local-tts-bridge]] - Rust local TTS bridge
- [[building-blocks/sidecar-server]] - Sidecar server
- [[building-blocks/tauri-core]] - Tauri core
