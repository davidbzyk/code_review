---
id: interfaces/pipeline-channel-events
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Channel Event Messages"
description: "The `PipelineEvent` and `DriveEvent` message shapes sent over Tauri channels."
domain: architecture
tags:
  - interface
  - channel
  - events
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/pipeline.rs
  - resource: src-tauri/src/google_drive.rs
  - resource: src/routes/preview/+page.svelte
---
# Channel Event Messages

Both enums serialize with `tag = "event"` and `content = "data"` in camelCase.

## PipelineEvent (src-tauri/src/pipeline.rs)
- `progress` with `stage` and `percent`.
- `complete` with `outputPath`.
- `error` with `message`.

## DriveEvent (src-tauri/src/google_drive.rs)
- `progress` with `percent`.
- `complete` with `url`.
- `error` with `message`.

## Receivers
`processViaTauri` and `uploadToDrive` declare matching TypeScript unions and assign `Channel.onmessage` (src/routes/preview/+page.svelte).

## Related
- [[interfaces/tauri-commands]]
- [[runtime/process-recording-desktop]]
- [[runtime/upload-to-drive]]
