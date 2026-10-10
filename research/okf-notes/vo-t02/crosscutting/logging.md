---
id: crosscutting/logging
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Logging"
description: "Rust `log` calls and the frontend `logger`."
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
  - resource: src-tauri/src/pipeline.rs
  - resource: src-tauri/src/local_tts.rs
related:
  - building-blocks/frontend-state
  - crosscutting/error-handling
---
# Logging

Logging is split between the Rust `log` crate and a console logger in the webview.

## Frontend
- `logger` (src/lib/logger.ts) prints to the console with the prefix `[VO:<category>]` and a colour per level (`debug`, `info`, `warn`, `error`).
- It has named helpers such as `configLoaded`, `recordingStart`, `elevenLabsTest`, `pipelineStage`, `driveUploadDone`, plus generic `info`, `warn`, `error`, `debug`.

## Backend
- `log::info!`, `log::warn!`, `log::error!` with tags such as `[pipeline]`, `[local_tts]`, `[elevenlabs]`, `[ffmpeg]`, `[config]`, `[secrets]`.
- `tauri_plugin_log` is added in `setup` only when `cfg!(debug_assertions)`, at level `Info` (src-tauri/src/lib.rs).
- `test_api_key` logs only the last four characters of the key (src-tauri/src/elevenlabs.rs).

## Related
- [Frontend State](../building-blocks/frontend-state.md)
- [Error Handling](./error-handling.md)
