---
id: crosscutting/logging
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Logging
description: Rust uses the log crate with tauri-plugin-log, the sidecar uses Python logging, and the UI uses a console logger.
domain: architecture
tags:
  - crosscutting
  - logging
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/lib.rs
  - resource: src/lib/logger.ts
  - resource: src-tauri/sidecar/server.py
  - resource: src-tauri/sidecar/tts.py
  - resource: src-tauri/sidecar/profiles.py
related:
  - building-blocks/frontend-shell
  - crosscutting/error-handling
  - building-blocks/tauri-core
---

# Logging

Each process logs on its own channel.

## Facts

- Rust: `log::info!`, `warn!`, `error!` with bracketed prefixes such as `[pipeline]`, `[sidecar]`, `[local_tts]`; `tauri_plugin_log` is set to `LevelFilter::Info` in setup (src-tauri/src/lib.rs).
- Frontend: `logger` writes `[VO:category]` console lines with a time stamp and a colour per level; helper methods cover config, recording, ElevenLabs, pipeline and Drive events (src/lib/logger.ts).
- Sidecar: `logging.basicConfig` at INFO, logger name `voiceover-tts`, child loggers `voiceover-tts.engine` and `voiceover-tts.profiles` (server.py, tts.py, profiles.py).
- The watchdog writes to `<data-dir>/logs/watchdog.log` (server.py).
- Sidecar stdout is discarded and stderr is inherited by the host (src-tauri/src/sidecar.rs).

## Related

- [[building-blocks/frontend-shell]] - Frontend shell and utilities
- [[crosscutting/error-handling]] - Error handling
- [[building-blocks/tauri-core]] - Tauri core
