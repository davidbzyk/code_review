---
id: crosscutting/logging
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Logging
description: Log output in the frontend, Rust host and Python sidecar.
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
  - resource: src-tauri/src/sidecar.rs
related:
  - building-blocks/frontend-state-and-config
  - crosscutting/error-handling
---

# Logging

Each process logs separately.

## Facts

- Frontend: `logger` writes `console[level]` with the prefix `[VO:<category>]` and a `HH:MM:SS.mmm` stamp; levels `info`, `warn`, `error`, `debug` (src/lib/logger.ts).
- Named helpers cover config, recording, ElevenLabs, pipeline and Drive events (`configLoaded`, `recordingStart`, `pipelineStage`, `driveUploadDone` and others).
- Rust: the `log` crate with `tauri_plugin_log` at `LevelFilter::Info` (src-tauri/src/lib.rs); messages carry tags such as `[pipeline]`, `[sidecar]`, `[local_tts]`.
- The sidecar child has stdout set to null and stderr inherited (src-tauri/src/sidecar.rs).
- Python: `logging.basicConfig` at INFO, logger name `voiceover-tts` (src-tauri/sidecar/server.py); uvicorn runs at `log_level="warning"`.
- The watchdog writes `logs/watchdog.log` under the data dir (`_start_parent_watchdog`).
- Sidecar modules use loggers `voiceover-tts.engine`, `voiceover-tts.profiles`, `voiceover-tts.chunked`.

## Related

- [Frontend State and Config](../building-blocks/frontend-state-and-config.md)
- [Error Handling](./error-handling.md)
