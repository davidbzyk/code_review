---
id: interfaces/pipeline-events
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Channel event messages"
description: "PipelineEvent and DriveEvent message shapes sent over Tauri channels."
domain: architecture
tags:
  - interfaces
  - channel
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
architecture_layer: interfaces
sources:
  - resource: src-tauri/src/pipeline.rs
  - resource: src-tauri/src/google_drive.rs
  - resource: src/routes/preview/+page.svelte
related:
  - interfaces/tauri-commands
  - runtime/process-recording-desktop-flow
  - runtime/google-drive-upload-flow
---

# Channel event messages

Two enums are serialized as `{ event, data }` objects with camelCase variant names.

## PipelineEvent (src-tauri/src/pipeline.rs)
- `progress` with `stage: string`, `percent: number`
- `complete` with `output_path`
- `error` with `message`

## DriveEvent (src-tauri/src/google_drive.rs)
- `progress` with `percent`
- `complete` with `url`
- `error` with `message`

## Consumers (src/routes/preview/+page.svelte)
- `processViaTauri()` types the union and updates `appState.processingProgress` and `processingStage` on `progress`, `outputPath` on `complete`.
- `uploadToDrive()` reads `complete` to set `driveLink`.
- Field names inside `data` follow the Rust struct field names; the page reads `outputPath` from the complete message.

## Related

- [[interfaces/tauri-commands]]
- [[runtime/process-recording-desktop-flow]]
- [[runtime/google-drive-upload-flow]]
