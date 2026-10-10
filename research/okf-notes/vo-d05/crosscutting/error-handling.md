---
id: crosscutting/error-handling
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Error handling
description: Rust commands return Result<_, String>, the sidecar returns JSON error bodies, and the UI shows messages.
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
  - resource: src-tauri/sidecar/server.py
  - resource: src/routes/preview/+page.svelte
  - resource: src/lib/drive.ts
related:
  - crosscutting/logging
  - interfaces/sidecar-http-routes
  - building-blocks/tauri-media-pipeline
---

# Error handling

Errors travel as strings from Rust to the page and as `{"error": ...}` bodies from the sidecar.

## Facts

- Tauri commands return `Result<T, String>`; messages are built with `map_err(|e| format!(...))` (src-tauri/src/pipeline.rs, src-tauri/src/local_tts.rs).
- `local_tts::poll_and_download` returns an error on status `error` or after the timeout.
- The sidecar's `error_response(status, message)` returns JSON with `error`; generation failures set status `error` and the message (src-tauri/sidecar/server.py).
- `/models/download` streams SSE events with `progress` -1 on failure; `download_model` turns that into a `ModelDownloadEvent::Error`.
- `processAndSave` catches errors into `processingError` (src/routes/preview/+page.svelte).
- `DriveUploadError` keeps the HTTP status for a 401 retry (src/lib/drive.ts).
- Cleanup routines ignore removal failures after logging a warning (`cleanup_stale_recordings`).

## Related

- [[crosscutting/logging]] - Logging
- [[interfaces/sidecar-http-routes]] - Sidecar HTTP routes
- [[building-blocks/tauri-media-pipeline]] - Rust media pipeline
