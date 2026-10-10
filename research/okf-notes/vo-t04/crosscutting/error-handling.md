---
id: crosscutting/error-handling
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Error handling"
description: "Rust commands return Result<_, String> and the frontend turns thrown errors into messages shown on the page."
domain: architecture
tags:
  - crosscutting
  - errors
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/pipeline.rs
  - resource: src-tauri/src/ffmpeg.rs
  - resource: src-tauri/src/elevenlabs.rs
  - resource: src-tauri/src/google_drive.rs
  - resource: src-tauri/src/commands/recording.rs
  - resource: src/routes/+page.svelte
  - resource: src/routes/preview/+page.svelte
  - resource: src/routes/settings/+page.svelte
relations:
  relates_to:
    - crosscutting/logging
    - interfaces/tauri-commands
    - runtime/process-recording-tauri
---
# Error handling

Errors are strings at the Rust boundary and `errorMessage` or local state in the pages.

## Rust

- Commands use `Result<T, String>` and map causes with `map_err(|e| e.to_string())` or `format!` (src-tauri/src/commands/recording.rs, src-tauri/src/google_drive.rs).
- ffmpeg failures return `ffmpeg <step> failed: <stderr>` (src-tauri/src/ffmpeg.rs).
- Non-success ElevenLabs responses return `ElevenLabs API error <status>: <body>` (src-tauri/src/elevenlabs.rs).
- `process_recording` returns `Recording file not found`, `ElevenLabs API key not set`, or `No voice configured` (src-tauri/src/pipeline.rs).
- Progress sends and cleanup use `.ok()` to ignore failures.

## Frontend

- src/routes/+page.svelte writes failures to `appState.errorMessage`, resets `recordingState` to `ready`, and shows a dismissible message.
- src/routes/preview/+page.svelte sets `processingError` in `processAndSave` and `uploadToDrive`.
- src/routes/settings/+page.svelte uses `testError` and `driveError`.

## Related

[[crosscutting/logging]], [[interfaces/tauri-commands]], [[runtime/process-recording-tauri]]
