---
id: glossary/terms
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Glossary"
description: "Terms that appear in the code, each with the file that defines it."
domain: architecture
tags:
  - glossary
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/lib/state.svelte.ts
  - resource: src/lib/recorder.svelte.ts
  - resource: src-tauri/src/pipeline.rs
  - resource: src-tauri/src/elevenlabs.rs
  - resource: src-tauri/src/google_drive.rs
  - resource: src-tauri/src/config.rs
  - resource: src-tauri/src/ffmpeg.rs
  - resource: src-tauri/src/commands/recording.rs
  - resource: src-tauri/src/commands/window.rs
  - resource: src-tauri/src/prerequisites.rs
relations:
  relates_to:
    - building-blocks/frontend-state
    - building-blocks/rust-media-pipeline
    - interfaces/tauri-commands
---
# Glossary

One line per term.

- `AppState` / `appState`: reactive singleton for config and recording state (src/lib/state.svelte.ts).
- `RecordingState`: union of eight phase names (src/lib/state.svelte.ts).
- `isTauri()`: detects the desktop webview (src/lib/state.svelte.ts).
- `CaptureMode`: `fullscreen`, `window`, `region` (src/lib/recorder.svelte.ts).
- Session id: `rec-<time>-<random>` folder name for chunks (src/lib/recorder.svelte.ts, validated in src-tauri/src/commands/recording.rs).
- Chunk: one `chunk_NNNN.webm` file (src-tauri/src/commands/recording.rs).
- `PipelineEvent`: progress, complete, error message for `process_recording` (src-tauri/src/pipeline.rs).
- S2S: ElevenLabs speech-to-speech (`S2S_BASE_URL`, src-tauri/src/elevenlabs.rs).
- `Voice`: id, name, description, default flag (src-tauri/src/config.rs).
- `DriveTokens`, `DriveEvent`: Drive token set and upload messages (src-tauri/src/google_drive.rs).
- PKCE: code verifier and S256 challenge (src-tauri/src/google_drive.rs).
- Sidecar: the bundled `ffmpeg` binary found by `resolve_ffmpeg_path` (src-tauri/src/ffmpeg.rs).
- `PrerequisiteStatus`: ffmpeg availability and version (src-tauri/src/prerequisites.rs).
- Widget: the small `widget` window created by `create_widget_window` (src-tauri/src/commands/window.rs).

## Related

[[building-blocks/frontend-state]], [[building-blocks/rust-media-pipeline]], [[interfaces/tauri-commands]]
