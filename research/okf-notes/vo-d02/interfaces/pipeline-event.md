---
id: interfaces/pipeline-event
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Channel event messages
description: PipelineEvent and DriveEvent shapes sent through Tauri channels.
domain: architecture
tags:
  - interfaces
  - events
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/pipeline.rs
  - resource: src-tauri/src/google_drive.rs
  - resource: src/routes/preview/+page.svelte
related:
  - interfaces/tauri-commands
  - runtime/process-recording-desktop
  - runtime/drive-upload
---

Both enums use serde `rename_all = "camelCase"`, `tag = "event"`, `content = "data"`.

## PipelineEvent (src-tauri/src/pipeline.rs)
- `{ event: "progress", data: { stage, percent } }`
- `{ event: "complete", data: { outputPath } }`
- `{ event: "error", data: { message } }`

Stages sent: "Saving", "Extracting audio", "Transforming voice", "Assembling video".

## DriveEvent (src-tauri/src/google_drive.rs)
- `{ event: "progress", data: { percent } }`
- `{ event: "complete", data: { url } }`
- `{ event: "error", data: { message } }`

## Consumers
`processViaTauri()` and `uploadToDrive()` in src/routes/preview/+page.svelte declare matching TypeScript union types and assign `onEvent.onmessage`.

## Related
[[interfaces/tauri-commands]], [[runtime/process-recording-desktop]], [[runtime/drive-upload]]
