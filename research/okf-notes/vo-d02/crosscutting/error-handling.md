---
id: crosscutting/error-handling
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Error handling
description: How Rust and TypeScript report failures to the user.
domain: architecture
tags:
  - crosscutting
  - arc42-8
  - errors
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/pipeline.rs
  - resource: src-tauri/src/ffmpeg.rs
  - resource: src-tauri/src/commands/recording.rs
  - resource: src/routes/+page.svelte
  - resource: src/routes/preview/+page.svelte
  - resource: src/routes/settings/+page.svelte
related:
  - interfaces/pipeline-event
  - crosscutting/logging
  - building-blocks/backend-pipeline
---

Rust functions return `Result<T, String>`; the frontend turns failures into messages in `appState` or page state.

## Rust
- Commands map errors with `map_err(|e| e.to_string())` or a formatted message (src-tauri/src/commands/recording.rs, src-tauri/src/config.rs).
- ffmpeg helpers return the child's stderr text in the `Err` string (src-tauri/src/ffmpeg.rs).
- `validate_session_id` rejects unsafe ids before building paths.
- `PipelineEvent::Error` and `DriveEvent::Error` exist as channel messages; `DriveEvent::Error` is sent on a failed upload.
- Sends on a channel use `.ok()`, ignoring send failures.

## TypeScript
- src/routes/+page.svelte: `try/catch` around `startRecording` sets `appState.errorMessage` and resets state to `ready`.
- src/routes/preview/+page.svelte: `processAndSave` stores the message in `processingError`; `uploadToDrive` does the same with `String(err)`.
- src/routes/settings/+page.svelte: `testApiKey` sets `keyValid` false and `testError`; `connectDrive` sets `driveError`.
- `loadConfig` and `saveConfig` catch failures and call `logger.error`.

## Related
[[interfaces/pipeline-event]], [[crosscutting/logging]], [[building-blocks/backend-pipeline]]
