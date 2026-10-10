---
id: interfaces/tauri-events
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Tauri Events and Channels"
description: "Message formats sent over Tauri channels and window events."
domain: architecture
tags:
  - interfaces
  - tauri
  - events
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/pipeline.rs
  - resource: src-tauri/src/google_drive.rs
  - resource: src/routes/widget/+page.svelte
  - resource: src/routes/preview/+page.svelte
relations:
  relates_to:
    - building-blocks/route-widget
    - interfaces/tauri-commands-services
---

Two channel formats and four widget events cross the Rust and webview boundary.

## Channels

- `PipelineEvent` (`src-tauri/src/pipeline.rs`): JSON `{ "event": "progress", "data": { "stage", "percent" } }`, `{ "event": "complete", "data": { "outputPath" } }`, `{ "event": "error", "data": { "message" } }`.
- `DriveEvent` (`src-tauri/src/google_drive.rs`): `progress` with `percent`, `complete` with `url`, `error` with `message`.
- The page reads both through `Channel.onmessage` in `src/routes/preview/+page.svelte`, with matching TypeScript union types.

## Window events

| Event | Sent by | Listener in the code |
|---|---|---|
| `recording-pause` | widget page via `plugin:event\|emit` | none |
| `recording-resume` | widget page | none |
| `recording-stop` | widget page `emit` | none |
| `recording-cancel` | widget page `emit` | none |
| `widget-voice-name` | no sender in the code | widget page `listen` |

"None" means a search of `src/` and `src-tauri/src/` found no listener.

## Related

- [Widget route](../building-blocks/route-widget.md)
- [Tauri commands, services](tauri-commands-services.md)
