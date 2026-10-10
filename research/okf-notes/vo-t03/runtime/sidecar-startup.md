---
id: runtime/sidecar-startup
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Sidecar startup and restart"
description: "How the host launches the TTS sidecar and keeps it healthy."
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
  - building-blocks/rust-sidecar-client
  - building-blocks/sidecar-server
  - interfaces/sidecar-cli-arguments
---
# Sidecar startup and restart

The host starts the sidecar at launch in a background task and restarts it on demand.

## Steps

1. `run()` (src-tauri/src/lib.rs) spawns `sidecar::start_sidecar` after `app.manage(SidecarState::default())`.
2. `start_sidecar` sets `starting` and calls `start_sidecar_inner` (src-tauri/src/sidecar.rs).
3. `find_available_port` binds `127.0.0.1:0` and reads the port.
4. `resolve_sidecar_path` returns the bundled `voiceover-tts` binary in release builds; in debug builds it returns none.
5. Without a binary, `resolve_dev_server_path` finds `sidecar/server.py` and runs it with `.sidecar-venv` python, a local `.venv` python, or `python3`.
6. The arguments are `--port`, `--data-dir`, `--parent-pid`, `--ffmpeg`.
7. The host polls `health_check` (GET `/health`, expects `status` equal to `healthy`) every 500 ms for up to 60 s; on timeout it calls `stop_sidecar_inner`; if the child exits it returns an error.
8. `ensure_running` is called before each sidecar request: it waits while `starting` is set, returns the port when healthy, else stops and restarts.
9. In the sidecar, `main` starts the watchdog thread and `uvicorn.run`.

## Related

- [[building-blocks/rust-sidecar-client]]
- [[building-blocks/sidecar-server]]
- [[interfaces/sidecar-cli-arguments]]
