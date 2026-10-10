---
id: runtime/sidecar-startup
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Flow: Sidecar Startup and Health
description: How Rust starts, health-checks and restarts the Python sidecar.
domain: architecture
tags:
  - runtime
  - flow
  - sidecar
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/lib.rs
  - resource: src-tauri/src/sidecar.rs
  - resource: src-tauri/sidecar/server.py
relations:
  relates_to:
    - building-blocks/rust-local-tts-and-sidecar
    - building-blocks/rust-app-shell
    - building-blocks/sidecar-server
---
# Flow: Sidecar Startup and Health

This flow runs at app launch and again whenever a command needs the sidecar.

1. `run` in `src-tauri/src/lib.rs` spawns `sidecar::start_sidecar` in the background.
2. `start_sidecar` sets `starting`, calls `start_sidecar_inner`, then clears `starting` and calls `notify_waiters`.
3. `start_sidecar_inner` picks a free port with `find_available_port` and the app data dir as `--data-dir`.
4. `resolve_sidecar_path` returns the bundled `voiceover-tts` binary in release builds; in debug builds it returns `None` and the code runs `server.py` with a `.sidecar-venv` Python or `python3`.
5. The child gets `--port`, `--data-dir`, `--parent-pid`, `--ffmpeg`.
6. The loop polls `health_check` every 500 ms for up to 60 s and stops the child on timeout.
7. `main()` in `server.py` starts the parent watchdog and `uvicorn`.
8. Later commands call `ensure_running`: it waits if `starting` is set, returns the port when `health_check` passes, else stops the child and calls `start_sidecar`.
9. `poll_generation` and `get_generation_audio` use `get_port` without a health check.

## Related

- [Rust Local TTS and Sidecar Manager](../building-blocks/rust-local-tts-and-sidecar.md)
- [Rust App Shell](../building-blocks/rust-app-shell.md)
- [Sidecar Server](../building-blocks/sidecar-server.md)
