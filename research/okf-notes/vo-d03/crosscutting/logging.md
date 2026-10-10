---
id: crosscutting/logging
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Logging"
description: "Console logger in the frontend and the log crate with tauri-plugin-log in Rust."
domain: architecture
tags:
  - crosscutting
  - logging
  - arc42-8
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/lib/logger.ts
  - resource: src-tauri/src/lib.rs
  - resource: src-tauri/src/pipeline.rs
  - resource: src-tauri/src/elevenlabs.rs
  - resource: src/routes/+layout.svelte
relations:
  relates_to:
    - building-blocks/frontend-logger
    - crosscutting/error-handling
---

# Logging

Frontend code logs to the browser console; Rust code logs with the `log` macros.

## Frontend

`logger` in `src/lib/logger.ts` prints `[VO:<category>]` lines with colours per level. It is used by `src/lib/state.svelte.ts`, `src/lib/recorder.svelte.ts`, `src/routes/preview/+page.svelte` and `src/routes/settings/+page.svelte`. `src/routes/+layout.svelte` uses `console.error` for the prerequisite check failure.

## Rust

- `src-tauri/src/lib.rs` registers `tauri_plugin_log` at `LevelFilter::Info` only when `cfg!(debug_assertions)`.
- `pipeline.rs` logs with prefix `[pipeline]` (`log::info!`, `log::warn!`), including total elapsed time.
- `elevenlabs.rs` logs with prefix `[elevenlabs]`: request size, status, elapsed time, and the first six and last four characters of the key in `test_api_key`.
- `lib.rs` logs `log::error!` when ffmpeg is not found at startup.

## Related

- [building-blocks/frontend-logger](../building-blocks/frontend-logger.md)
- [crosscutting/error-handling](./error-handling.md)
- [crosscutting/secrets](./secrets.md)
