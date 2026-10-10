---
id: crosscutting/logging
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Logging"
description: "The Rust `log` calls and the frontend `logger` helper."
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
---
# Logging

Logging exists on both sides with category prefixes.

## Facts
- Frontend: `logger` writes to `console` with prefix `[VO:{category}]` and a time stamp; levels `debug`, `info`, `warn`, `error` (src/lib/logger.ts).
- Rust: `log::info!`, `log::warn!`, `log::error!` with prefixes `[pipeline]` and `[elevenlabs]` (src-tauri/src/pipeline.rs, src-tauri/src/elevenlabs.rs).
- `tauri_plugin_log` is installed only when `cfg!(debug_assertions)` (src-tauri/src/lib.rs).
- Users: src/routes/preview/+page.svelte, src/routes/settings/+page.svelte, src/lib/state.svelte.ts, src/lib/recorder.svelte.ts.

## Related
- [[building-blocks/frontend-state]]
- [[crosscutting/error-handling]]
- [[crosscutting/secrets-handling]]
