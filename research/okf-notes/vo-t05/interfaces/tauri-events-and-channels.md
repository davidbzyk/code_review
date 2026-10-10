---
id: interfaces/tauri-events-and-channels
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Channels and Window Events
description: Typed channel messages from Rust to the webview and window events between pages.
domain: architecture
tags:
  - interface
  - events
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/pipeline.rs
  - resource: src-tauri/src/models.rs
  - resource: src-tauri/src/google_drive.rs
  - resource: src/routes/widget/+page.svelte
  - resource: src/routes/preview/+page.svelte
related:
  - interfaces/commands-pipeline-models-drive
  - runtime/process-recording-elevenlabs
  - crosscutting/error-handling
---

# Channels and Window Events

Long commands send tagged enums over `tauri::ipc::Channel`; serde uses `tag = "event"`, `content = "data"`, `rename_all = "camelCase"`.

| Enum | Variants | Declared in |
|---|---|---|
| `PipelineEvent` | `Progress { stage, percent }`, `Complete { output_path }`, `Error { message }` | src-tauri/src/pipeline.rs |
| `ModelDownloadEvent` | `Progress { progress, status }`, `Complete { model }`, `Error { message }` | src-tauri/src/models.rs |
| `DriveEvent` | `Progress { percent }`, `Complete { url }`, `Error { message }` | src-tauri/src/google_drive.rs |

The page declares matching TypeScript unions and assigns `onEvent.onmessage` (src/routes/preview/+page.svelte).

## Window events (src/routes/widget/+page.svelte)

- Listens for `widget-voice-name` (payload string).
- Emits `recording-pause`, `recording-resume`, `recording-stop`, `recording-cancel`.
- Invokes `close_widget_window` after stop or cancel.

## Related

- [Tauri Commands: Pipeline, Models, Drive, ElevenLabs](./commands-pipeline-models-drive.md)
- [Flow: Process a Recording (ElevenLabs)](../runtime/process-recording-elevenlabs.md)
- [Error Handling](../crosscutting/error-handling.md)
