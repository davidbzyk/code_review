---
id: glossary/terms
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Glossary"
description: "Terms used in the code, each with its defining file."
domain: architecture
tags:
  - glossary
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/lib/state.svelte.ts
  - resource: src/lib/recorder.svelte.ts
  - resource: src/lib/logger.ts
  - resource: src-tauri/src/pipeline.rs
  - resource: src-tauri/src/google_drive.rs
  - resource: src-tauri/src/config.rs
  - resource: src-tauri/src/elevenlabs.rs
  - resource: src-tauri/src/prerequisites.rs
  - resource: src-tauri/src/commands/window.rs
---
# Glossary

One line per term.

- `AppConfig`: persisted settings object (src-tauri/src/config.rs).
- `appState`: shared reactive state singleton (src/lib/state.svelte.ts).
- `RecordingState`: union of recording stages (src/lib/state.svelte.ts).
- `CaptureMode`: `fullscreen`, `window`, `region` (src/lib/recorder.svelte.ts).
- `Voice`: ElevenLabs voice entry with `is_default` (src-tauri/src/config.rs).
- `S2S`: speech-to-speech conversion (src-tauri/src/elevenlabs.rs).
- `PipelineEvent`: progress messages of `process_recording` (src-tauri/src/pipeline.rs).
- `DriveEvent`: progress messages of `upload_to_drive` (src-tauri/src/google_drive.rs).
- `DriveTokens`: OAuth result (src-tauri/src/google_drive.rs).
- `PrerequisiteStatus`: ffmpeg availability (src-tauri/src/prerequisites.rs).
- `widget`: label of the floating window (src-tauri/src/commands/window.rs).
- `logger`: console logger with `[VO:` prefix (src/lib/logger.ts).
- `session_id`: names a recording's chunk folder (src-tauri/src/commands/recording.rs).

## Related
- [[building-blocks/frontend-state]]
- [[interfaces/tauri-commands]]
- [[context/system-context]]
