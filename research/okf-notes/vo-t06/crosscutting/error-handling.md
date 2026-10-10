---
id: crosscutting/error-handling
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Error Handling"
description: "How failures are returned in Rust and shown in the pages."
domain: architecture
tags:
  - crosscutting
  - errors
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/pipeline.rs
  - resource: src-tauri/src/commands/recording.rs
  - resource: src/routes/+page.svelte
  - resource: src/routes/preview/+page.svelte
  - resource: src/lib/drive.ts
relations:
  relates_to:
    - crosscutting/logging
    - building-blocks/rust-pipeline
---

Rust commands return `Result<T, String>`; the pages catch rejections and keep a message in state.

## Facts

- Rust functions build messages with `map_err` and `format!`, for example "ElevenLabs API error {status}: {body}" (`src-tauri/src/elevenlabs.rs`).
- ffmpeg failures return the stderr text (`src-tauri/src/ffmpeg.rs`).
- Progress sends use `.ok()`, so a closed channel does not fail the command (`src-tauri/src/pipeline.rs`).
- Cleanup calls such as `fs::remove_dir_all(...).ok()` ignore errors (`src-tauri/src/commands/recording.rs`).
- `startRecording` calls `cleanup()` and rethrows on error; the record route sets `appState.errorMessage` and returns to `ready` (`src/routes/+page.svelte`).
- The preview route stores messages in `processingError` and logs through `logger.pipelineError` or `logger.driveError`.
- `DriveUploadError` carries the HTTP status so the 401 case can retry (`src/lib/drive.ts`).
- `extractAudioFromBlob` falls back to sending the WebM when decoding fails.

## Related

- [Logging](logging.md)
- [Rust pipeline](../building-blocks/rust-pipeline.md)
