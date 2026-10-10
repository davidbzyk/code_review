---
id: interfaces/events-and-channels
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Events and Channels"
description: "Streaming message types between Rust and the webview."
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
  - resource: src/routes/widget/+page.svelte
related:
  - interfaces/tauri-commands-recording-and-pipeline
  - interfaces/tauri-commands-providers
  - crosscutting/error-handling
---
# Events and Channels

Two Rust enums are sent over Tauri `Channel`s, and the widget uses named events.

## PipelineEvent (src-tauri/src/pipeline.rs)
Serialized with `tag = "event"`, `content = "data"`, camelCase names:
- `progress` with `stage: String`, `percent: f32`
- `complete` with `output_path: String` (the TypeScript type reads `outputPath`)
- `error` with `message: String`

## DriveEvent (src-tauri/src/google_drive.rs)
- `progress` with `percent`
- `complete` with `url`
- `error` with `message`

The preview page handles both types in `onEvent.onmessage` (src/routes/preview/+page.svelte).

## Widget events (src/routes/widget/+page.svelte)
- Emitted: `recording-stop`, `recording-cancel`, `recording-pause`, `recording-resume`.
- Listened: `widget-voice-name`, payload a string.
- No `listen` for the emitted names and no emit of `widget-voice-name` appear in src.

## Related
- [Tauri Commands: Recording and Pipeline](./tauri-commands-recording-and-pipeline.md)
- [Tauri Commands: Config, Providers and Drive](./tauri-commands-providers.md)
- [Error Handling](../crosscutting/error-handling.md)
