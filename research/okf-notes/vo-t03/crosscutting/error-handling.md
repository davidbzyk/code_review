---
id: crosscutting/error-handling
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Error handling"
description: "How errors are produced and shown across layers."
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
  - resource: src/routes/+page.svelte
  - resource: src/routes/preview/+page.svelte
  - resource: src/lib/drive.ts
related:
  - crosscutting/logging
  - interfaces/pipeline-events
---
# Error handling

Rust commands return `Result<T, String>`; the webview shows the string.

## Facts

- Rust functions turn library errors into messages with `map_err(|e| format!(...))` (pipeline.rs, local_tts.rs, ffmpeg.rs).
- HTTP failures read the response body and include it in the error text (elevenlabs.rs, local_tts.rs).
- `process_recording` returns early with messages such as "Recording file not found" and "ElevenLabs API key not set — configure in Settings".
- Channel sends use `.ok()`, so a closed channel is ignored.
- The sidecar returns `JSONResponse` with `{"error": ...}` and status 400, 404 or 500 (server.py); generation errors are stored in `_generations[id]["error"]`.
- The main page copies thrown errors into `appState.errorMessage`, shown with a dismiss button (src/routes/+page.svelte).
- The preview page keeps `processingError`; `DriveUploadError` carries `status` so a 401 can trigger one retry (src/lib/drive.ts).
- A track `ended` event during recording cancels the recording and sets "Screen sharing was stopped" (src/lib/recorder.svelte.ts).

## Related

- [[crosscutting/logging]]
- [[interfaces/pipeline-events]]
