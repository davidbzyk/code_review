---
id: interfaces/pipeline-events
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Channel event messages"
description: "The tagged event enums sent from Rust to the webview over Tauri channels."
domain: architecture
tags:
  - interface
  - events
  - channel
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/pipeline.rs
  - resource: src-tauri/src/models.rs
  - resource: src-tauri/src/google_drive.rs
  - resource: src/routes/preview/+page.svelte
related:
  - interfaces/tauri-commands
  - building-blocks/rust-pipeline
---
# Channel event messages

Three enums use `#[serde(rename_all = "camelCase", tag = "event", content = "data")]`, so each message is `{event, data}`.

## Messages

- `PipelineEvent` (src-tauri/src/pipeline.rs): `progress` with `stage`, `percent`; `complete` with `outputPath`; `error` with `message`.
- `ModelDownloadEvent` (src-tauri/src/models.rs): `progress` with `progress`, `status`; `complete` with `model`; `error` with `message`.
- `DriveEvent` (src-tauri/src/google_drive.rs): `progress` with `percent`; `complete` with `url`; `error` with `message`.

## Consumers

The preview page defines matching TypeScript unions for `PipelineEvent` and `DriveEvent` and sets `Channel.onmessage` (src/routes/preview/+page.svelte).

## Window events

The widget page listens for `widget-voice-name` and emits `recording-stop`, `recording-cancel`, `recording-pause` and `recording-resume` (src/routes/widget/+page.svelte).

## Related

- [[interfaces/tauri-commands]]
- [[building-blocks/rust-pipeline]]
