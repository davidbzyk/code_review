---
id: crosscutting/error-handling
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Error handling"
description: "How Rust and TypeScript code report failures to callers and to the user."
domain: architecture
tags:
  - crosscutting
  - errors
  - arc42-8
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/pipeline.rs
  - resource: src-tauri/src/ffmpeg.rs
  - resource: src-tauri/src/elevenlabs.rs
  - resource: src-tauri/src/google_drive.rs
  - resource: src-tauri/src/commands/recording.rs
  - resource: src/routes/preview/+page.svelte
  - resource: src/routes/+page.svelte
  - resource: src/lib/recorder.svelte.ts
relations:
  relates_to:
    - crosscutting/logging
    - building-blocks/backend-pipeline
---

# Error handling

Rust commands return `Result<_, String>`; the frontend catches rejections and stores a message.

## Rust

- Every command listed in [tauri-commands](../interfaces/tauri-commands.md) except `get_temp_dir` returns `Result<_, String>`, built with `map_err(|e| e.to_string())` or a formatted message.
- `ffmpeg.rs` returns `ffmpeg ... failed: <stderr>` when the exit status is non-zero.
- `elevenlabs.rs` and `google_drive.rs` include the HTTP status or response body in the error text.
- `pipeline.rs` and `google_drive.rs` send `Error` events with `.ok()`, ignoring send failures.
- `commands/recording.rs` rejects bad session ids in `validate_session_id`.

## TypeScript

- `src/routes/+page.svelte` catches in `handleRecord` and `handleStop` and writes `appState.errorMessage`.
- `src/routes/preview/+page.svelte` catches in `processAndSave` and `uploadToDrive` and writes `processingError`.
- `src/lib/recorder.svelte.ts` calls `cleanup()` and rethrows when `startRecording` fails.
- `loadConfig` in `src/lib/state.svelte.ts` wraps each source in `try/catch` and logs through `logger.error`.

## Related

- [crosscutting/logging](./logging.md)
- [building-blocks/backend-pipeline](../building-blocks/backend-pipeline.md)
- [interfaces/pipeline-events](../interfaces/pipeline-events.md)
