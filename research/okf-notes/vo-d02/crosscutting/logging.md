---
id: crosscutting/logging
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Logging
description: Console logger in the frontend and log macros in Rust.
domain: architecture
tags:
  - crosscutting
  - arc42-8
  - logging
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/lib/logger.ts
  - resource: src-tauri/src/lib.rs
  - resource: src-tauri/src/pipeline.rs
  - resource: src-tauri/src/elevenlabs.rs
related:
  - building-blocks/frontend-state-and-logging
  - crosscutting/error-handling
---

Frontend logs go to the browser console; Rust logs use the `log` crate with `tauri_plugin_log` in debug builds.

## Frontend
- `logger` in src/lib/logger.ts prints `[VO:<category>]` lines; categories include config, record, elevenlabs, pipeline, drive, ffmpeg.
- Levels: debug, info, warn, error, each with its own colour.
- Used by src/lib/recorder.svelte.ts, src/lib/state.svelte.ts, src/routes/preview/+page.svelte and src/routes/settings/+page.svelte.

## Rust
- src-tauri/src/lib.rs adds `tauri_plugin_log` at `LevelFilter::Info` only when `cfg!(debug_assertions)`.
- `log::info!`, `log::warn!` and `log::error!` appear in src-tauri/src/pipeline.rs (prefix `[pipeline]`) and src-tauri/src/elevenlabs.rs (prefix `[elevenlabs]`).
- Startup logs "ffmpeg not found on system PATH" when the check fails.

## Related
[[building-blocks/frontend-state-and-logging]], [[crosscutting/error-handling]]
