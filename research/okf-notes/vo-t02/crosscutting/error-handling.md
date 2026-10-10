---
id: crosscutting/error-handling
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Error Handling"
description: "How errors travel from Rust commands to the interface."
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
  - resource: src-tauri/src/elevenlabs.rs
  - resource: src/routes/preview/+page.svelte
  - resource: src/routes/+page.svelte
  - resource: src/lib/drive.ts
related:
  - interfaces/events-and-channels
  - crosscutting/logging
---
# Error Handling

Rust commands return `Result<_, String>`; the pages show the message.

## Facts
- Commands map errors with `map_err` into strings, for example `format!("ElevenLabs API error {status}: {body}")` (src-tauri/src/elevenlabs.rs).
- `validate_session_id` rejects empty ids and any character other than alphanumeric, `-` and `_` (src-tauri/src/commands/recording.rs).
- `read_file_bytes` returns "Access denied" outside the allowed folders.
- Failed ffmpeg runs return the stderr text (src-tauri/src/ffmpeg.rs).
- `PipelineEvent::Error` exists; `process_recording` returns `Err` and sends `Progress` and `Complete` events.
- `processAndSave` catches errors into `processingError` (src/routes/preview/+page.svelte).
- `handleRecord` and `handleStop` write `appState.errorMessage` (src/routes/+page.svelte).
- `DriveUploadError` keeps the HTTP status for a retry on 401 (src/lib/drive.ts).

## Related
- [Events and Channels](../interfaces/events-and-channels.md)
- [Logging](./logging.md)
