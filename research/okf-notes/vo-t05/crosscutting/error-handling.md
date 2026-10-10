---
id: crosscutting/error-handling
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Error Handling
description: How errors are typed, returned and shown across Rust, TypeScript and Python.
domain: architecture
tags:
  - crosscutting
  - errors
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/pipeline.rs
  - resource: src-tauri/src/local_tts.rs
  - resource: src/lib/drive.ts
  - resource: src/routes/preview/+page.svelte
  - resource: src-tauri/sidecar/server.py
  - resource: src-tauri/src/models.rs
related:
  - interfaces/tauri-events-and-channels
  - building-blocks/rust-pipeline
  - crosscutting/logging
---

# Error Handling

Each layer reports failure in its own form.

## Rust

- Commands return `Result<T, String>`; messages are built with `format!` and `map_err` (src-tauri/src/pipeline.rs, src-tauri/src/local_tts.rs).
- `PipelineEvent::Error`, `ModelDownloadEvent::Error` and `DriveEvent::Error` are channel variants (src-tauri/src/pipeline.rs, src-tauri/src/models.rs, src-tauri/src/google_drive.rs).
- `send_with_timeout` in local_tts.rs wraps requests with a seconds limit and a message prefix.
- ffmpeg failures return the decoded stderr text (src-tauri/src/ffmpeg.rs).

## TypeScript

- `DriveUploadError(status, body)` carries the HTTP status (src/lib/drive.ts).
- `/preview` stores messages in `processingError`; `/` stores them in `appState.errorMessage`.
- `+layout.svelte` shows an `error-banner` when ffmpeg is unavailable.

## Python

- `error_response(status, message)` returns `JSONResponse` with `{"error": message}` (src-tauri/sidecar/server.py).
- Generation failures set `_generations[id]["status"] = "error"` and `error`.
- Model download errors are sent as SSE with `progress: -1`.

## Related

- [Channels and Window Events](../interfaces/tauri-events-and-channels.md)
- [Rust Pipeline and ffmpeg](../building-blocks/rust-pipeline.md)
- [Logging](./logging.md)
