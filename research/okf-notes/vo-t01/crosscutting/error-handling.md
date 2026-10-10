---
id: crosscutting/error-handling
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Error Handling
description: How errors travel between Python, Rust and the webview.
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
  - resource: src/routes/(app)/preview/+page.svelte
  - resource: src/lib/drive.ts
relations:
  relates_to:
    - building-blocks/rust-pipeline
    - interfaces/tauri-commands-tts
    - interfaces/sidecar-http-api
---
# Error Handling

Rust commands return `Result<T, String>`; the webview shows the message text.

## Facts

- Commands in `src-tauri/src/` return `Result<_, String>`, with `map_err` building the text; `get_temp_dir` returns a plain `String`.
- `send_with_timeout` in `src-tauri/src/local_tts.rs` turns a timeout into a message such as "timed out after Ns".
- The sidecar returns `{"error": message}` through `error_response` in `src-tauri/sidecar/server.py`.
- A failed generation stores `status: "error"` and the exception text in `_generations`; the status route returns both.
- `poll_and_download` returns an error when the status is `error` or the deadline passes.
- `PipelineEvent::Error` and `ModelDownloadEvent::Error` exist for channel errors.
- `processAndSave` catches errors, sets `processingError`, and calls `logger.pipelineError` (`src/routes/(app)/preview/+page.svelte`).
- `DriveUploadError` keeps the HTTP status (`src/lib/drive.ts`).
- Cleanup deletions use `.ok()` to ignore failures.

## Related

- [Rust Pipeline and ffmpeg](../building-blocks/rust-pipeline.md)
- [Tauri Commands: Local TTS, Models, Sidecar](../interfaces/tauri-commands-tts.md)
- [Sidecar HTTP API](../interfaces/sidecar-http-api.md)
