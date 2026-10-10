---
id: crosscutting/logging
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Logging"
description: "Rust log macros and the TypeScript logger."
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
relations:
  relates_to:
    - building-blocks/frontend-drive-logger
    - crosscutting/error-handling
---

Rust uses the `log` crate; the webview uses `logger` from `src/lib/logger.ts`.

## Facts

- `tauri_plugin_log` is added only when `cfg!(debug_assertions)`, with level `Info` (`src-tauri/src/lib.rs`).
- Rust messages carry a bracketed prefix such as `[pipeline]`, `[elevenlabs]`, `[config]`, `[secrets]`, `[ffmpeg]`.
- `logger` prints `[VO:<category>]` lines to the console with a time stamp; levels `debug`, `info`, `warn`, `error` (`src/lib/logger.ts`).
- Categories seen in calls: `config`, `record`, `webcam`, `elevenlabs`, `pipeline`, `drive`, `preview`, `ffmpeg`.
- `src/lib/logger.test.ts` tests the output.
- Users of `logger`: `state.svelte.ts`, `recorder.svelte.ts`, `drive.ts`, preview and settings routes.

## Related

- [Frontend drive helper and logger](../building-blocks/frontend-drive-logger.md)
- [Error handling](error-handling.md)
