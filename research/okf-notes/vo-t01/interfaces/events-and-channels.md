---
id: interfaces/events-and-channels
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Events and Channels
description: Streaming message shapes sent from Rust to the webview and window events.
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
  - resource: src/lib/voicebox.ts
  - resource: src/lib/RecordingCard.svelte
relations:
  relates_to:
    - interfaces/tauri-commands-app
    - interfaces/tauri-commands-tts
    - runtime/record-and-process-recording
---
# Events and Channels

Long commands take a Tauri `Channel` and send tagged enums serialized with `event` and `data` keys.

## Channel enums

- `PipelineEvent`: `progress` with `stage` and `percent`; `complete` with `outputPath`; `error` with `message` (`src-tauri/src/pipeline.rs`). Receiver: preview page.
- `ModelDownloadEvent`: `progress` with `progress` and `status`; `complete` with `model`; `error` with `message` (`src-tauri/src/models.rs`). Receiver: `VoiceboxClient.downloadModel`.
- `DriveEvent`: `progress` with `percent`; `complete` with `url`; `error` with `message` (`src-tauri/src/google_drive.rs`). Receiver: `handleUploadToDrive`.

## Window events

The widget page listens for `widget-voice-name` and emits `recording-stop`, `recording-cancel`, `recording-pause`, `recording-resume` (`src/routes/widget/+page.svelte`). No `listen` for the stop, cancel, pause or resume events appears in the other files under `src/`.

## Related

- [Tauri Commands: Config, Recording, Library, Drive, Window](tauri-commands-app.md)
- [Tauri Commands: Local TTS, Models, Sidecar](tauri-commands-tts.md)
- [Flow: Record and Process a Recording](../runtime/record-and-process-recording.md)
