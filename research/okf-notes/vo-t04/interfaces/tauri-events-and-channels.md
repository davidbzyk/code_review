---
id: interfaces/tauri-events-and-channels
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Events and channels"
description: "Progress and window control travel as PipelineEvent and DriveEvent channel messages and as three named window events."
domain: architecture
tags:
  - interface
  - events
  - messages
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/pipeline.rs
  - resource: src-tauri/src/google_drive.rs
  - resource: src/routes/preview/+page.svelte
  - resource: src/routes/widget/+page.svelte
relations:
  relates_to:
    - interfaces/tauri-commands
    - runtime/process-recording-tauri
    - runtime/widget-window-flow
---
# Events and channels

Messages are tagged unions serialised as `{ "event": <name>, "data": {...} }`.

## Channel messages

- `PipelineEvent` (src-tauri/src/pipeline.rs), `rename_all = "camelCase"`: `progress { stage, percent }`, `complete { outputPath }`, `error { message }`. The `Error` variant is marked `#[allow(dead_code)]`.
- `DriveEvent` (src-tauri/src/google_drive.rs): `progress { percent }`, `complete { url }`, `error { message }`.
- The frontend declares matching TypeScript unions and sets `onEvent.onmessage` (src/routes/preview/+page.svelte).

## Window events (src/routes/widget/+page.svelte)

| Event | Direction | Payload |
|---|---|---|
| `widget-voice-name` | listened by widget | string |
| `recording-pause`, `recording-resume` | emitted by widget through `plugin:event|emit` | null |
| `recording-stop` | emitted by widget with `emit` | none |
| `recording-cancel` | emitted by widget with `emit` | none |

No `listen` for the stop, cancel, pause or resume events appears in src.

## Related

[[interfaces/tauri-commands]], [[runtime/process-recording-tauri]], [[runtime/widget-window-flow]]
