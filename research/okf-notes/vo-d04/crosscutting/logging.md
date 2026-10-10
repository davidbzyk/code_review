---
id: crosscutting/logging
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Logging"
description: "Frontend console logger and Rust log macros."
domain: architecture
tags:
  - crosscutting
  - logging
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
architecture_layer: crosscutting
sources:
  - resource: src/lib/logger.ts
  - resource: src-tauri/src/lib.rs
  - resource: src-tauri/src/pipeline.rs
  - resource: src-tauri/src/elevenlabs.rs
related:
  - building-blocks/frontend-logger
  - crosscutting/error-handling
---

# Logging

The frontend logs through `logger`; the backend uses the `log` crate.

## Facts
- `logger` prefixes `[VO:<category>]` (src/lib/logger.ts).
- Rust code calls `log::info!`, `log::warn!`, `log::error!` with prefixes `[pipeline]` and `[elevenlabs]` (src-tauri/src/pipeline.rs, src-tauri/src/elevenlabs.rs).
- `tauri_plugin_log` is attached only when `cfg!(debug_assertions)` (src-tauri/src/lib.rs).
- `test_api_key` logs the first six and last four characters of the key (src-tauri/src/elevenlabs.rs).

## Related

- [[building-blocks/frontend-logger]]
- [[crosscutting/error-handling]]
