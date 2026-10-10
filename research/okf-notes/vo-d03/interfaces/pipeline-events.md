---
id: interfaces/pipeline-events
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Progress event channels"
description: "PipelineEvent and DriveEvent message shapes sent over Tauri channels."
domain: architecture
tags:
  - interface
  - tauri
  - events
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/pipeline.rs
  - resource: src-tauri/src/google_drive.rs
  - resource: src/routes/preview/+page.svelte
relations:
  relates_to:
    - interfaces/tauri-commands
    - runtime/process-recording-desktop
---

# Progress event channels

Two Rust enums are serialized as `{ event, data }` objects and delivered to `Channel.onmessage` in the page.

## PipelineEvent (`src-tauri/src/pipeline.rs`)

| `event` | `data` |
|---|---|
| `progress` | `stage: string`, `percent: number` |
| `complete` | `outputPath: string` |
| `error` | `message: string` |

Stages sent by `process_recording`: "Saving", "Extracting audio", "Transforming voice", "Assembling video".

## DriveEvent (`src-tauri/src/google_drive.rs`)

| `event` | `data` |
|---|---|
| `progress` | `percent: number` |
| `complete` | `url: string` |
| `error` | `message: string` |

## Receiver

`processViaTauri()` and `uploadToDrive()` in `src/routes/preview/+page.svelte` declare matching TypeScript union types and assign `onEvent.onmessage`. The `PipelineEvent` enum carries `#[allow(dead_code)]`.

## Related

- [interfaces/tauri-commands](./tauri-commands.md)
- [runtime/process-recording-desktop](../runtime/process-recording-desktop.md)
- [runtime/upload-to-drive](../runtime/upload-to-drive.md)
