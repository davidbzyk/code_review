---
id: crosscutting/logging
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Logging
description: Log output in the webview, Rust core and sidecar.
domain: architecture
tags:
  - crosscutting
  - logging
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/lib/logger.ts
  - resource: src-tauri/src/lib.rs
  - resource: src-tauri/sidecar/server.py
relations:
  relates_to:
    - building-blocks/frontend-service-clients
    - building-blocks/rust-app-shell
---
# Logging

Each of the three processes logs on its own channel.

## Facts

- `src/lib/logger.ts` exports `logger`, whose methods call `console` with the prefix `[VO:<category>]` and a time stamp. It has named methods (`configLoaded`, `recordingStart`, `pipelineStage`, `driveConnect`) and generic `info`, `warn`, `error`, `debug`.
- Rust uses the `log` macros with tags such as `[pipeline]`, `[sidecar]`, `[local_tts]`; `tauri_plugin_log` is set to `Info` in `run()` (`src-tauri/src/lib.rs`).
- The sidecar uses `logging.basicConfig` at `INFO`, with loggers `voiceover-tts` and `watchdog`; the watchdog also writes `<data-dir>/logs/watchdog.log` (`src-tauri/sidecar/server.py`).
- The sidecar stdout is discarded and stderr is inherited (`start_sidecar_inner` in `src-tauri/src/sidecar.rs`).

## Related

- [Frontend Service Clients](../building-blocks/frontend-service-clients.md)
- [Rust App Shell](../building-blocks/rust-app-shell.md)
