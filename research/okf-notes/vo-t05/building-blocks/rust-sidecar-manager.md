---
id: building-blocks/rust-sidecar-manager
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Rust Sidecar Manager
description: Starts, health-checks, restarts and stops the Python TTS child process.
domain: architecture
tags:
  - building-block
  - rust
  - sidecar
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/sidecar.rs
related:
  - runtime/sidecar-startup
  - building-blocks/sidecar-server
  - building-blocks/rust-tts-providers
  - building-blocks/rust-pipeline
---

# Rust Sidecar Manager

`sidecar.rs` owns the child process behind a `SidecarState` of async mutexes.

## Facts

- `SidecarState` fields: `child`, `port`, `data_dir`, `starting`, `startup_done` (`Notify`).
- `start_sidecar(app)` sets `starting`, runs `start_sidecar_inner`, then notifies waiters.
- `start_sidecar_inner` picks a free port with `find_available_port`, uses `app_data_dir` as data dir, and passes `--port --data-dir --parent-pid --ffmpeg`.
- `resolve_sidecar_path()` returns the bundled `voiceover-tts` next to the executable, except in debug builds, where it returns `None`.
- In that case `resolve_dev_server_path()` finds `sidecar/server.py` and the code runs it with `.sidecar-venv/bin/python3`, a local `.venv`, or `python3`.
- `HEALTH_CHECK_TIMEOUT_SECS` is 60 and `HEALTH_CHECK_INTERVAL_MS` is 500.
- `health_check(port)` GETs `/health` and expects `"status": "healthy"`.
- `ensure_running(app)` waits for a startup in progress, reuses a healthy port, or restarts.
- `stop_sidecar`, `get_port`, and command `get_sidecar_status` returning `running`, `healthy`, `port`.

## Used by

`local_tts.rs`, `models.rs`, `pipeline.rs`, `lib.rs`.

## Related

- [Flow: Sidecar Startup and Shutdown](../runtime/sidecar-startup.md)
- [Sidecar Server](./sidecar-server.md)
- [Rust TTS Providers and Models](./rust-tts-providers.md)
- [Rust Pipeline and ffmpeg](./rust-pipeline.md)
