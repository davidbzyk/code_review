---
id: crosscutting/error-handling
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Error handling"
description: "How errors travel from Rust commands to the pages."
domain: architecture
tags:
  - crosscutting
  - errors
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
architecture_layer: crosscutting
sources:
  - resource: src-tauri/src/pipeline.rs
  - resource: src-tauri/src/ffmpeg.rs
  - resource: src-tauri/src/commands/recording.rs
  - resource: src/routes/+page.svelte
  - resource: src/routes/preview/+page.svelte
  - resource: src/routes/settings/+page.svelte
related:
  - crosscutting/logging
  - interfaces/pipeline-events
  - interfaces/tauri-commands
---

# Error handling

Rust commands return `Result<_, String>`; pages catch the rejection and show text.

## Facts
- Backend functions map errors with `map_err(|e| e.to_string())` or `format!` messages (src-tauri/src/commands/recording.rs, src-tauri/src/ffmpeg.rs).
- `PipelineEvent::Error` and `DriveEvent::Error` exist as channel variants (src-tauri/src/pipeline.rs, src-tauri/src/google_drive.rs).
- Home page catches into `appState.errorMessage`, shown with a dismiss button (src/routes/+page.svelte).
- Preview page keeps `processingError`, logs with `logger.pipelineError`, and shows a Dismiss button (src/routes/preview/+page.svelte).
- Settings page uses `driveError` and `testError` (src/routes/settings/+page.svelte).
- The layout shows `error-banner` when ffmpeg is missing (src/routes/+layout.svelte).

## Related

- [[crosscutting/logging]]
- [[interfaces/pipeline-events]]
- [[interfaces/tauri-commands]]
