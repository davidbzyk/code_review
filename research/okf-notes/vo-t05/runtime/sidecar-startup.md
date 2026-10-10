---
id: runtime/sidecar-startup
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Flow: Sidecar Startup and Shutdown
description: How the app launches the TTS child process and how the child exits.
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
  - building-blocks/rust-sidecar-manager
  - building-blocks/sidecar-server
  - building-blocks/rust-app-shell
---

# Flow: Sidecar Startup and Shutdown

Trigger: the Tauri `setup` closure in `run()` (src-tauri/src/lib.rs).

1. `setup` manages `SidecarState` and spawns `sidecar::start_sidecar` on `tauri::async_runtime`.
2. `start_sidecar_inner` calls `find_available_port` and `create_dir_all` on the app data dir (src-tauri/src/sidecar.rs).
3. `resolve_sidecar_path` or `resolve_dev_server_path` picks the binary or `server.py`; the child is spawned with `--port`, `--data-dir`, `--parent-pid`, `--ffmpeg`.
4. The loop sleeps 500 ms, calls `health_check`, and checks `try_wait` on the child, until 60 seconds pass.
5. In the child, `main()` (server.py) sets `DATA_DIR`, `HF_HUB_CACHE`, `PATH`, calls `_start_parent_watchdog`, and runs uvicorn.
6. `lifespan` calls `_cleanup_generations` and starts `_generation_worker`.
7. Later commands call `ensure_running`: wait if `starting`, return the port if healthy, otherwise `stop_sidecar_inner` and `start_sidecar`.
8. On exit of the parent, `_watch` in server.py sees the PID gone and sends `SIGTERM` to itself (`os._exit(0)` on Windows).

## Related

- [Rust Sidecar Manager](../building-blocks/rust-sidecar-manager.md)
- [Sidecar Server](../building-blocks/sidecar-server.md)
- [Rust App Shell](../building-blocks/rust-app-shell.md)
