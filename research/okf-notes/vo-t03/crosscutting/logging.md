---
id: crosscutting/logging
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Logging"
description: "Logger setup in the webview, the Rust host and the sidecar."
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
  - resource: src-tauri/src/pipeline.rs
related:
  - crosscutting/error-handling
  - building-blocks/frontend-state-and-utils
---
# Logging

Each layer logs with its own mechanism.

## Facts

- Webview: `logger` in src/lib/logger.ts writes to `console` with prefix `[VO:<category>]`, a time stamp and a colour per level.
- Host: `tauri_plugin_log` at level `Info` (src-tauri/src/lib.rs); modules call `log::info!`, `log::warn!`, `log::error!` with bracketed tags such as `[pipeline]`, `[sidecar]`, `[local_tts]`, `[elevenlabs]`, `[secrets]`.
- Sidecar: `logging.basicConfig(level=INFO)` with logger `voiceover-tts`; a separate `watchdog` logger writes `<data_dir>/logs/watchdog.log` (src-tauri/sidecar/server.py).
- The host starts the sidecar with stdout discarded and stderr inherited (src-tauri/src/sidecar.rs).

## Related

- [[crosscutting/error-handling]]
- [[building-blocks/frontend-state-and-utils]]
