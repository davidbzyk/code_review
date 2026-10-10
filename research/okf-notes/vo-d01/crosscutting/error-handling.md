---
id: crosscutting/error-handling
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Error Handling"
description: "How errors are returned and shown across the Rust and Svelte layers."
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
  - resource: src/routes/preview/+page.svelte
  - resource: src/routes/+page.svelte
---
# Error Handling

Rust commands return `Result<_, String>`; the frontend turns rejections into text state.

## Facts
- Command errors are built with `map_err(|e| e.to_string())` or `format!` (src-tauri/src/pipeline.rs, src-tauri/src/elevenlabs.rs).
- ffmpeg failures return `ffmpeg ... failed: {stderr}` (src-tauri/src/ffmpeg.rs).
- Channel sends use `.ok()`, so send failures are ignored (src-tauri/src/pipeline.rs).
- `processAndSave` catches errors into `processingError` and logs `pipelineError` (src/routes/preview/+page.svelte).
- `handleRecord` and `handleStop` write `appState.errorMessage` and reset the state to `ready` (src/routes/+page.svelte).
- `startRecording` calls `cleanup()` before rethrowing (src/lib/recorder.svelte.ts).

## Related
- [[crosscutting/logging]]
- [[interfaces/pipeline-channel-events]]
- [[building-blocks/media-pipeline]]
