---
id: crosscutting/logging
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Logging"
description: "Rust uses the log crate with tauri-plugin-log in debug builds, and the frontend uses the logger object over console."
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
  - resource: src-tauri/src/elevenlabs.rs
  - resource: src-tauri/src/ffmpeg.rs
relations:
  relates_to:
    - building-blocks/frontend-logger
    - crosscutting/error-handling
    - crosscutting/secrets-handling
---
# Logging

Two logging paths exist, one per language.

## Rust

- `log::info!`, `log::warn!` and `log::error!` calls carry bracketed prefixes `[pipeline]`, `[elevenlabs]`, `[ffmpeg]` (src-tauri/src/pipeline.rs, src-tauri/src/elevenlabs.rs, src-tauri/src/ffmpeg.rs).
- `tauri_plugin_log` is added only when `cfg!(debug_assertions)` is true, at `LevelFilter::Info` (src-tauri/src/lib.rs).

## Frontend

- `logger` in src/lib/logger.ts prints `[VO:<category>]` messages; the header comment says to filter by `[VO:` in the console.
- Categories seen in callers: `config`, `record`, `elevenlabs`, `pipeline`, `drive`, `ffmpeg`, `preview`.

## Used by

src/lib/state.svelte.ts, src/lib/recorder.svelte.ts, src/routes/preview/+page.svelte, src/routes/settings/+page.svelte.

## Related

[[building-blocks/frontend-logger]], [[crosscutting/error-handling]], [[crosscutting/secrets-handling]]
